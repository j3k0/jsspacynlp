"""FastAPI application for jsspacynlp lemmatization service."""

# Import spacy-transformers early to register transformer components
# This must happen before any spacy.load() calls
try:
    import spacy_transformers  # noqa: F401
except ImportError:
    pass  # spacy-transformers is optional, only needed for transformer models

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

import spacy
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .config import settings
from .models import model_registry
from .schemas import (
    ErrorResponse,
    HealthResponse,
    InfoResponse,
    LemmatizeRequest,
    LemmatizeResponse,
    ModelInfo,
    ModelsResponse,
)

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Track startup time
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting jsspacynlp server v{__version__}")
    logger.info(f"spaCy version: {spacy.__version__}")

    # Load models from config
    config_dir = Path(settings.models_config_dir)
    config_file = config_dir / settings.models_config_file
    default_config_file = config_dir / settings.models_config_default

    # Try config.json first, fall back to config.default.json
    if config_file.exists():
        logger.info(f"Looking for model config at: {config_file}")
        config_to_load = config_file
    elif default_config_file.exists():
        logger.info(f"config.json not found, using default: {default_config_file}")
        config_to_load = default_config_file
    else:
        logger.warning(f"No config files found at {config_file} or {default_config_file}")
        logger.warning("Server will start without models")
        config_to_load = None

    if config_to_load:
        try:
            model_registry.load_from_config(config_to_load)
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            logger.warning("Server will start without models")

    loaded_models = model_registry.list_models()
    if loaded_models:
        logger.info(f"Loaded models: {', '.join(loaded_models)}")
    else:
        logger.warning("No models loaded. Please check configuration.")

    logger.info("Server startup complete")

    yield

    # Shutdown
    logger.info("Shutting down jsspacynlp server")


# Create FastAPI app
app = FastAPI(
    title="jsspacynlp",
    description="Fast lemmatization service powered by spaCy",
    version=__version__,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "name": "jsspacynlp",
        "version": __version__,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint.

    Returns:
        Service health status and loaded models
    """
    uptime = time.time() - startup_time

    return HealthResponse(
        status="healthy",
        models_loaded=model_registry.list_models(),
        uptime_seconds=uptime
    )


@app.get("/info", response_model=InfoResponse)
async def info():
    """Service information endpoint.

    Returns:
        Service metadata and version information
    """
    return InfoResponse(
        name="jsspacynlp",
        version=__version__,
        spacy_version=spacy.__version__,
        models_loaded=len(model_registry.list_models())
    )


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    """List available models endpoint.

    Returns:
        List of loaded models with metadata
    """
    model_names = model_registry.list_models()
    model_infos = []

    for name in model_names:
        info = model_registry.get_model_info(name)
        if info:
            model_infos.append(ModelInfo(**info))

    return ModelsResponse(available_models=model_infos)


@app.post("/lemmatize", response_model=LemmatizeResponse)
async def lemmatize(request: LemmatizeRequest):
    """Lemmatize text using spaCy.

    Args:
        request: Lemmatization request with model name, texts, and optional fields

    Returns:
        Compact JSON format with annotations and tokens

    Raises:
        HTTPException: If model not found or processing fails
    """
    start_time = time.time()

    # Validate model exists
    nlp = model_registry.get_model(request.model)
    if not nlp:
        available = model_registry.list_models()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Model '{request.model}' not found",
                "available_models": available
            }
        )

    # Validate batch size
    if len(request.texts) > settings.max_batch_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Batch size {len(request.texts)} exceeds maximum {settings.max_batch_size}"
            }
        )

    # Validate text lengths
    for i, text in enumerate(request.texts):
        if len(text) > settings.max_text_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": f"Text at index {i} exceeds maximum length {settings.max_text_length}"
                }
            )

    # Define available fields and their extractors
    field_extractors = {
        'text': lambda token: token.text,
        'lemma': lambda token: token.lemma_,
        'pos': lambda token: token.pos_,
        'tag': lambda token: token.tag_,
        'dep': lambda token: token.dep_,
        'ent_type': lambda token: token.ent_type_,
        'is_alpha': lambda token: str(token.is_alpha),
        'is_stop': lambda token: str(token.is_stop),
    }

    # Determine which fields to include
    if request.fields:
        # Validate requested fields
        invalid_fields = set(request.fields) - set(field_extractors.keys())
        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": f"Invalid fields: {', '.join(invalid_fields)}",
                    "available_fields": list(field_extractors.keys())
                }
            )
        annotations = request.fields
    else:
        # Default fields (must-haves + commonly used)
        annotations = ['text', 'lemma', 'pos', 'tag', 'dep']

    # Process texts in batch
    try:
        docs = list(nlp.pipe(request.texts))
    except Exception as e:
        logger.error(f"Error processing texts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error processing texts", "details": str(e)}
        )

    # Convert to compact format
    all_tokens = []
    for doc in docs:
        doc_tokens = []
        for token in doc:
            token_data = [field_extractors[field](token) for field in annotations]
            doc_tokens.append(token_data)
        all_tokens.append(doc_tokens)

    processing_time = (time.time() - start_time) * 1000  # Convert to ms

    return LemmatizeResponse(
        annotations=annotations,
        tokens=all_tokens,
        model=request.model,
        processing_time_ms=processing_time
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

