"""Integration tests for jsspacynlp server.

These tests require a running server instance.
Run with: docker-compose up -d && pytest tests/test_integration.py
"""

import pytest
import requests
import time


# Server URL - can be overridden with environment variable
SERVER_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def wait_for_server():
    """Wait for server to be ready."""
    max_retries = 30
    retry_delay = 1

    for i in range(max_retries):
        try:
            response = requests.get(f"{SERVER_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"\nServer is ready after {i + 1} attempts")
                return
        except requests.exceptions.RequestException:
            pass

        if i < max_retries - 1:
            time.sleep(retry_delay)

    pytest.skip("Server not available for integration tests")


@pytest.mark.integration
def test_server_health(wait_for_server):
    """Test server health endpoint."""
    response = requests.get(f"{SERVER_URL}/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "models_loaded" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))


@pytest.mark.integration
def test_server_info(wait_for_server):
    """Test server info endpoint."""
    response = requests.get(f"{SERVER_URL}/info")

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "jsspacynlp"
    assert "version" in data
    assert "spacy_version" in data
    assert "models_loaded" in data


@pytest.mark.integration
def test_list_models(wait_for_server):
    """Test models listing endpoint."""
    response = requests.get(f"{SERVER_URL}/models")

    assert response.status_code == 200
    data = response.json()

    assert "available_models" in data
    assert isinstance(data["available_models"], list)


@pytest.mark.integration
def test_lemmatize_with_available_model(wait_for_server):
    """Test lemmatization if models are available."""
    # First check what models are available
    response = requests.get(f"{SERVER_URL}/models")
    models_data = response.json()

    if not models_data["available_models"]:
        pytest.skip("No models loaded on server")

    # Use the first available model
    model_name = models_data["available_models"][0]["name"]

    # Test lemmatization
    response = requests.post(
        f"{SERVER_URL}/lemmatize",
        json={
            "model": model_name,
            "texts": ["Hello world", "Testing lemmatization"],
            "fields": ["text", "lemma", "pos"]
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "annotations" in data
    assert "tokens" in data
    assert "model" in data
    assert "processing_time_ms" in data

    assert data["model"] == model_name
    assert data["annotations"] == ["text", "lemma", "pos"]
    assert len(data["tokens"]) == 2  # Two input texts

    # Check first document has tokens
    assert len(data["tokens"][0]) > 0

    # Check token structure
    first_token = data["tokens"][0][0]
    assert len(first_token) == 3  # text, lemma, pos


@pytest.mark.integration
def test_lemmatize_invalid_model(wait_for_server):
    """Test lemmatization with invalid model."""
    response = requests.post(
        f"{SERVER_URL}/lemmatize",
        json={
            "model": "nonexistent_model_12345",
            "texts": ["Hello world"]
        }
    )

    assert response.status_code == 400
    data = response.json()

    assert "error" in data
    assert "nonexistent_model_12345" in data["error"]


@pytest.mark.integration
def test_lemmatize_empty_texts(wait_for_server):
    """Test lemmatization with empty texts array."""
    response = requests.post(
        f"{SERVER_URL}/lemmatize",
        json={
            "model": "test_model",
            "texts": []
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.integration
def test_lemmatize_batch(wait_for_server):
    """Test batch lemmatization if models available."""
    response = requests.get(f"{SERVER_URL}/models")
    models_data = response.json()

    if not models_data["available_models"]:
        pytest.skip("No models loaded on server")

    model_name = models_data["available_models"][0]["name"]

    # Create batch of 50 texts
    texts = [f"Test sentence number {i}" for i in range(50)]

    response = requests.post(
        f"{SERVER_URL}/lemmatize",
        json={
            "model": model_name,
            "texts": texts
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["tokens"]) == 50
    assert data["processing_time_ms"] > 0


@pytest.mark.integration
def test_api_documentation(wait_for_server):
    """Test that API documentation is accessible."""
    # Check OpenAPI JSON
    response = requests.get(f"{SERVER_URL}/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert "openapi" in openapi
    assert "paths" in openapi

    # Check Swagger UI (should return HTML)
    response = requests.get(f"{SERVER_URL}/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

