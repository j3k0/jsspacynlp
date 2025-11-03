"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import model_registry, ModelConfig


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_model(monkeypatch):
    """Mock a simple spaCy model for testing."""
    import spacy
    from spacy.tokens import Doc
    from spacy.vocab import Vocab

    # Create a simple blank model
    nlp = spacy.blank("en")
    
    # Add a simple lemmatizer
    vocab = nlp.vocab
    
    # Mock tokens with lemmas
    class MockToken:
        def __init__(self, text, lemma, pos="NOUN", tag="NN", dep="ROOT"):
            self.text = text
            self.lemma_ = lemma
            self.pos_ = pos
            self.tag_ = tag
            self.dep_ = dep
            self.ent_type_ = ""
            self.is_alpha = text.isalpha()
            self.is_stop = False
    
    class MockDoc:
        def __init__(self, text):
            # Simple tokenization
            words = text.split()
            self.tokens = [
                MockToken(word, word.lower(), "NOUN", "NN", "ROOT")
                for word in words
            ]
        
        def __iter__(self):
            return iter(self.tokens)
    
    # Mock the nlp.pipe method
    def mock_pipe(texts):
        return [MockDoc(text) for text in texts]
    
    nlp.pipe = mock_pipe
    
    # Register the mock model
    config = ModelConfig(
        name="test_model",
        language="en",
        model_type="test",
        path="en_core_web_sm"
    )
    model_registry.models["test_model"] = nlp
    model_registry.configs["test_model"] = config
    
    yield nlp
    
    # Cleanup
    if "test_model" in model_registry.models:
        del model_registry.models["test_model"]
    if "test_model" in model_registry.configs:
        del model_registry.configs["test_model"]

