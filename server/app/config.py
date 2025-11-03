"""Configuration management for jsspacynlp server."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_prefix="JSSPACYNLP_", case_sensitive=False)

    # Model configuration
    models_config_dir: str = "/app/models"
    models_config_file: str = "config.json"
    models_config_default: str = "config.default.json"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    
    # Processing limits
    max_batch_size: int = 1000
    max_text_length: int = 1_000_000  # 1MB per text
    
    # Performance
    disable_pipeline_components: list[str] = ["parser", "ner"]
    
    # CORS
    cors_origins: list[str] = ["*"]


settings = Settings()

