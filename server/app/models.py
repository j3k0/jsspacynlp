"""Model management and loading."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

import spacy
from spacy.language import Language

from .config import settings

logger = logging.getLogger(__name__)


class ModelConfig:
    """Configuration for a single model."""

    def __init__(
        self,
        name: str,
        language: str,
        model_type: str,
        path: str,
        disable: Optional[list[str]] = None
    ):
        self.name = name
        self.language = language
        self.model_type = model_type
        self.path = path
        self.disable = disable or settings.disable_pipeline_components


class ModelRegistry:
    """Registry for managing spaCy models."""

    def __init__(self):
        self.models: Dict[str, Language] = {}
        self.configs: Dict[str, ModelConfig] = {}

    def load_from_config(self, config_path: Path) -> None:
        """Load models from configuration file.

        Args:
            config_path: Path to config.json file
        """
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            logger.info("No models will be loaded. Server will start without models.")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

        models_config = config_data.get('models', [])
        if not models_config:
            logger.warning("No models specified in config file")
            return

        logger.info(f"Loading {len(models_config)} models from config...")

        for model_data in models_config:
            try:
                config = ModelConfig(
                    name=model_data['name'],
                    language=model_data.get('language', 'unknown'),
                    model_type=model_data.get('type', 'standard'),
                    path=model_data['path'],
                    disable=model_data.get('disable')
                )
                self.load_model(config)
            except KeyError as e:
                logger.error(f"Invalid model config, missing key: {e}")
            except Exception as e:
                logger.error(f"Failed to load model {model_data.get('name', 'unknown')}: {e}")

        logger.info(f"Successfully loaded {len(self.models)} models")

    def load_model(self, config: ModelConfig) -> None:
        """Load a single spaCy model.

        Args:
            config: Model configuration
        """
        logger.info(f"Loading model '{config.name}' from '{config.path}'...")

        try:
            # Check if path is absolute or relative
            model_path = config.path
            if not os.path.isabs(model_path):
                # Try as spaCy model name first
                try:
                    nlp = spacy.load(model_path, disable=config.disable)
                except OSError:
                    # Try as relative path from models directory
                    models_dir = Path(settings.models_config_dir)
                    model_path = models_dir / model_path
                    nlp = spacy.load(str(model_path), disable=config.disable)
            else:
                nlp = spacy.load(model_path, disable=config.disable)

            self.models[config.name] = nlp
            self.configs[config.name] = config

            # Log active components
            active_components = nlp.pipe_names
            logger.info(
                f"Model '{config.name}' loaded successfully. "
                f"Active components: {', '.join(active_components)}"
            )

        except Exception as e:
            logger.error(f"Failed to load model '{config.name}': {e}")
            raise

    def get_model(self, name: str) -> Optional[Language]:
        """Get a loaded model by name.

        Args:
            name: Model name

        Returns:
            spaCy Language object or None if not found
        """
        return self.models.get(name)

    def get_model_config(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name.

        Args:
            name: Model name

        Returns:
            ModelConfig or None if not found
        """
        return self.configs.get(name)

    def list_models(self) -> list[str]:
        """Get list of loaded model names.

        Returns:
            List of model names
        """
        return list(self.models.keys())

    def get_model_info(self, name: str) -> Optional[dict]:
        """Get detailed information about a model.

        Args:
            name: Model name

        Returns:
            Dictionary with model information or None
        """
        nlp = self.get_model(name)
        config = self.get_model_config(name)

        if not nlp or not config:
            return None

        return {
            'name': config.name,
            'language': config.language,
            'type': config.model_type,
            'version': nlp.meta.get('version', 'unknown'),
            'components': nlp.pipe_names
        }


# Global model registry instance
model_registry = ModelRegistry()

