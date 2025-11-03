"""Pydantic schemas for request/response validation."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class LemmatizeRequest(BaseModel):
    """Request schema for lemmatization endpoint."""

    model: str = Field(..., description="Name of the spaCy model to use")
    texts: list[str] = Field(..., description="List of texts to process")
    fields: Optional[list[str]] = Field(
        default=None,
        description="Fields to include in response (default: all available)"
    )

    @field_validator('texts')
    @classmethod
    def validate_texts(cls, v):
        """Validate texts list."""
        if not v:
            raise ValueError("texts cannot be empty")
        if len(v) > 1000:  # Will be configurable via settings
            raise ValueError("Batch size exceeds maximum allowed")
        return v

    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        """Validate model name."""
        if not v or not v.strip():
            raise ValueError("model name cannot be empty")
        return v.strip()


class LemmatizeResponse(BaseModel):
    """Response schema for lemmatization endpoint."""

    annotations: list[str] = Field(..., description="List of field names in order")
    tokens: list[list[list[str]]] = Field(
        ...,
        description="List of documents, each containing tokens with field values"
    )
    model: str = Field(..., description="Model used for processing")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class ModelInfo(BaseModel):
    """Information about a loaded model."""

    name: str = Field(..., description="Model identifier")
    language: str = Field(..., description="Language code")
    type: str = Field(..., description="Model type (transformer, large, custom)")
    version: Optional[str] = Field(None, description="Model version")
    components: list[str] = Field(..., description="Active pipeline components")


class ModelsResponse(BaseModel):
    """Response schema for models endpoint."""

    available_models: list[ModelInfo] = Field(..., description="List of loaded models")


class HealthResponse(BaseModel):
    """Response schema for health endpoint."""

    status: str = Field(..., description="Service status")
    models_loaded: list[str] = Field(..., description="List of loaded model names")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class InfoResponse(BaseModel):
    """Response schema for info endpoint."""

    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    spacy_version: str = Field(..., description="spaCy version")
    models_loaded: int = Field(..., description="Number of models loaded")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    available_models: Optional[list[str]] = Field(
        None,
        description="Available models (for invalid model errors)"
    )

