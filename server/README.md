# jsspacynlp Server

FastAPI-based lemmatization service powered by spaCy.

## Features

- 🚀 Fast batch processing with spaCy
- 📦 Compact JSON response format (50-70% smaller than traditional formats)
- 🌍 Multi-language support via spaCy models
- 🔧 Custom model support
- 🐳 Docker-ready with health checks
- 📊 Automatic API documentation (OpenAPI/Swagger)

## Quick Start

### Using Docker

```bash
# Build the image
docker build -t jsspacynlp-server .

# Run with model configuration
docker run -p 8000:8000 \
  -v $(pwd)/../models:/app/models:ro \
  jsspacynlp-server
```

### Local Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Install a spaCy model for testing
python -m spacy download en_core_web_sm

# Run the server
uvicorn app.main:app --reload
```

## API Endpoints

### POST /lemmatize

Lemmatize text using spaCy models.

**Request:**
```json
{
  "model": "fr_dep_news_trf",
  "texts": ["L'avion vole.", "Le chat dort."],
  "fields": ["text", "lemma", "pos"]
}
```

**Response:**
```json
{
  "annotations": ["text", "lemma", "pos"],
  "tokens": [
    [
      ["L'", "le", "DET"],
      ["avion", "avion", "NOUN"],
      ["vole", "voler", "VERB"],
      [".", ".", "PUNCT"]
    ],
    [
      ["Le", "le", "DET"],
      ["chat", "chat", "NOUN"],
      ["dort", "dormir", "VERB"],
      [".", ".", "PUNCT"]
    ]
  ],
  "model": "fr_dep_news_trf",
  "processing_time_ms": 42.5
}
```

**Available Fields:**
- `text`: Token text (required)
- `lemma`: Lemmatized form (required)
- `pos`: Part-of-speech tag (required)
- `tag`: Fine-grained POS tag
- `dep`: Dependency relation
- `ent_type`: Named entity type
- `is_alpha`: Is alphabetic
- `is_stop`: Is stop word

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": ["fr_dep_news_trf", "en_core_web_trf"],
  "uptime_seconds": 3600.5
}
```

### GET /models

List available models.

**Response:**
```json
{
  "available_models": [
    {
      "name": "fr_dep_news_trf",
      "language": "fr",
      "type": "transformer",
      "version": "3.7.0",
      "components": ["tok2vec", "tagger", "lemmatizer"]
    }
  ]
}
```

### GET /info

Service information.

**Response:**
```json
{
  "name": "jsspacynlp",
  "version": "0.1.0",
  "spacy_version": "3.7.2",
  "models_loaded": 2
}
```

## Configuration

### Environment Variables

- `JSSPACYNLP_MODELS_CONFIG_DIR`: Path to models directory (default: `/app/models`)
- `JSSPACYNLP_MODELS_CONFIG_FILE`: Config file name (default: `config.json`)
- `JSSPACYNLP_HOST`: Server host (default: `0.0.0.0`)
- `JSSPACYNLP_PORT`: Server port (default: `8000`)
- `JSSPACYNLP_LOG_LEVEL`: Logging level (default: `info`)
- `JSSPACYNLP_MAX_BATCH_SIZE`: Maximum batch size (default: `1000`)
- `JSSPACYNLP_MAX_TEXT_LENGTH`: Maximum text length (default: `1000000`)

### Model Configuration

Create a `config.json` file in the models directory:

```json
{
  "models": [
    {
      "name": "fr_dep_news_trf",
      "language": "fr",
      "type": "transformer",
      "path": "fr_dep_news_trf",
      "disable": ["parser", "ner"]
    }
  ]
}
```

See `../models/README.md` for detailed configuration options.

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_main.py::test_lemmatize_success
```

## Performance

- Processes 1000+ words in <100ms (depending on model)
- Supports batch processing for efficiency
- Disabled unnecessary pipeline components (parser, NER)
- Async request handling

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid model, invalid fields)
- `422`: Validation error (malformed request)
- `500`: Server error

Error responses include details:

```json
{
  "error": "Model 'unknown_model' not found",
  "available_models": ["fr_dep_news_trf", "en_core_web_trf"]
}
```

## Development

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type check (optional)
mypy app/
```

## Documentation

- [API_REFERENCE.md](../API_REFERENCE.md) - Complete API reference
- [README.md](../README.md) - Overview and getting started
- [client/README.md](../client/README.md) - Client library details
- [models/README.md](../models/README.md) - Model configuration

## License

MIT License - See LICENSE file for details.

