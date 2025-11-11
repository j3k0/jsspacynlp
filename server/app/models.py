"""Model management and loading."""

import json
import logging
import os
import subprocess
import sys
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
        disable: Optional[list[str]] = None,
        download_url: Optional[str] = None,
        huggingface_repo: Optional[str] = None
    ):
        self.name = name
        self.language = language
        self.model_type = model_type
        self.path = path
        self.disable = disable or settings.disable_pipeline_components
        self.download_url = download_url
        self.huggingface_repo = huggingface_repo


class ModelRegistry:
    """Registry for managing spaCy models."""

    def __init__(self):
        self.models: Dict[str, Language] = {}
        self.configs: Dict[str, ModelConfig] = {}
        self.models_download_dir = Path(settings.models_cache_dir)
        # Ensure download directory exists
        self.models_download_dir.mkdir(parents=True, exist_ok=True)

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
                    disable=model_data.get('disable'),
                    download_url=model_data.get('download_url'),
                    huggingface_repo=model_data.get('huggingface_repo')
                )
                self.load_model(config)
            except KeyError as e:
                logger.error(f"Invalid model config, missing key: {e}")
            except Exception as e:
                logger.error(f"Failed to load model {model_data.get('name', 'unknown')}: {e}")

        logger.info(f"Successfully loaded {len(self.models)} models")

    def _download_model_from_url(self, config: ModelConfig) -> bool:
        """Download and install model from URL using pip.

        Args:
            config: Model configuration with download_url

        Returns:
            True if download successful, False otherwise
        """
        if not config.download_url:
            return False

        logger.info(f"Downloading model '{config.name}' from {config.download_url}...")

        try:
            # Use pip to install the model
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--no-cache-dir", config.download_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"Successfully downloaded model '{config.name}'")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download model from {config.download_url}: {e}")
            return False

    def _download_model_from_huggingface(self, config: ModelConfig) -> Optional[str]:
        """Download model from HuggingFace Hub.

        Args:
            config: Model configuration with huggingface_repo

        Returns:
            Path to downloaded model directory, or None if failed
        """
        if not config.huggingface_repo:
            return None

        logger.info(f"Downloading model '{config.name}' from HuggingFace: {config.huggingface_repo}...")

        try:
            from huggingface_hub import snapshot_download

            # Download to our models download directory
            model_dir = self.models_download_dir / config.name
            
            # Download the model
            downloaded_path = snapshot_download(
                repo_id=config.huggingface_repo,
                local_dir=str(model_dir),
                local_dir_use_symlinks=False
            )
            
            logger.info(f"Successfully downloaded model '{config.name}' to {downloaded_path}")
            return str(downloaded_path)
        except Exception as e:
            logger.error(f"Failed to download from HuggingFace {config.huggingface_repo}: {e}")
            return None

    def load_model(self, config: ModelConfig) -> None:
        """Load a single spaCy model, downloading if necessary.

        Args:
            config: Model configuration
        """
        logger.info(f"Loading model '{config.name}' from '{config.path}'...")

        # Try loading the model first
        model_loaded = False
        nlp = None

        try:
            # Check if path is absolute or relative
            model_path = config.path
            if not os.path.isabs(model_path):
                # Try as spaCy model name first
                try:
                    nlp = spacy.load(model_path, disable=config.disable)
                    model_loaded = True
                except OSError:
                    # Try as relative path from models directory
                    models_dir = Path(settings.models_config_dir)
                    model_path = models_dir / model_path
                    if Path(model_path).exists():
                        nlp = spacy.load(str(model_path), disable=config.disable)
                        model_loaded = True
            else:
                if Path(model_path).exists():
                    nlp = spacy.load(model_path, disable=config.disable)
                    model_loaded = True

        except Exception as e:
            logger.debug(f"Could not load model '{config.name}' from path: {e}")
            model_loaded = False

        # If model not found, try downloading it
        if not model_loaded:
            logger.info(f"Model '{config.name}' not found, attempting to download...")
            
            # Try download_url first (for pip-installable packages)
            if config.download_url:
                if self._download_model_from_url(config):
                    # Try loading again after download
                    try:
                        nlp = spacy.load(config.path, disable=config.disable)
                        model_loaded = True
                    except Exception as e:
                        logger.error(f"Failed to load model after download: {e}")
            
            # Try HuggingFace if URL download didn't work
            if not model_loaded and config.huggingface_repo:
                downloaded_path = self._download_model_from_huggingface(config)
                if downloaded_path:
                    try:
                        nlp = spacy.load(downloaded_path, disable=config.disable)
                        model_loaded = True
                    except Exception as e:
                        logger.error(f"Failed to load model from HuggingFace download: {e}")

        # Final check
        if not model_loaded or nlp is None:
            error_msg = f"Failed to load model '{config.name}' from any source"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Store the model
        self.models[config.name] = nlp
        self.configs[config.name] = config

        # Log active components
        active_components = nlp.pipe_names
        logger.info(
            f"Model '{config.name}' loaded successfully. "
            f"Active components: {', '.join(active_components)}"
        )

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

