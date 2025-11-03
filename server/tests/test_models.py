"""Tests for model management."""

import json
import tempfile
from pathlib import Path

import pytest

from app.models import ModelConfig, ModelRegistry


def test_model_config_creation():
    """Test ModelConfig creation."""
    config = ModelConfig(
        name="test_model",
        language="en",
        model_type="small",
        path="en_core_web_sm"
    )
    
    assert config.name == "test_model"
    assert config.language == "en"
    assert config.model_type == "small"
    assert config.path == "en_core_web_sm"


def test_model_registry_init():
    """Test ModelRegistry initialization."""
    registry = ModelRegistry()
    
    assert len(registry.models) == 0
    assert len(registry.configs) == 0
    assert registry.list_models() == []


def test_model_registry_list_models(mock_model):
    """Test listing models."""
    from app.models import model_registry
    
    models = model_registry.list_models()
    assert "test_model" in models


def test_model_registry_get_model(mock_model):
    """Test getting a model."""
    from app.models import model_registry
    
    nlp = model_registry.get_model("test_model")
    assert nlp is not None
    
    nlp_none = model_registry.get_model("nonexistent")
    assert nlp_none is None


def test_model_registry_get_model_info(mock_model):
    """Test getting model info."""
    from app.models import model_registry
    
    info = model_registry.get_model_info("test_model")
    assert info is not None
    assert info["name"] == "test_model"
    assert info["language"] == "en"
    assert info["type"] == "test"
    
    info_none = model_registry.get_model_info("nonexistent")
    assert info_none is None


def test_load_from_config_file_not_found():
    """Test loading from non-existent config file."""
    registry = ModelRegistry()
    
    # Should not raise, just log warning
    registry.load_from_config(Path("/nonexistent/config.json"))
    
    assert len(registry.models) == 0


def test_load_from_config_empty_models():
    """Test loading from config with no models."""
    registry = ModelRegistry()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"models": []}, f)
        config_path = Path(f.name)
    
    try:
        registry.load_from_config(config_path)
        assert len(registry.models) == 0
    finally:
        config_path.unlink()


def test_load_from_config_invalid_json():
    """Test loading from config with invalid JSON."""
    registry = ModelRegistry()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        config_path = Path(f.name)
    
    try:
        with pytest.raises(json.JSONDecodeError):
            registry.load_from_config(config_path)
    finally:
        config_path.unlink()

