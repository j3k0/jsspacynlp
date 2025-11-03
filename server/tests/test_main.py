"""Tests for main API endpoints."""

import pytest
from fastapi import status


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "name" in data
    assert data["name"] == "jsspacynlp"
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))


def test_info_endpoint(client):
    """Test info endpoint."""
    response = client.get("/info")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "jsspacynlp"
    assert "version" in data
    assert "spacy_version" in data
    assert "models_loaded" in data


def test_models_endpoint(client):
    """Test models list endpoint."""
    response = client.get("/models")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "available_models" in data
    assert isinstance(data["available_models"], list)


def test_lemmatize_no_model(client):
    """Test lemmatize endpoint with invalid model."""
    response = client.post(
        "/lemmatize",
        json={
            "model": "nonexistent_model",
            "texts": ["Hello world"]
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert "nonexistent_model" in data["error"]


def test_lemmatize_empty_texts(client):
    """Test lemmatize endpoint with empty texts."""
    response = client.post(
        "/lemmatize",
        json={
            "model": "test_model",
            "texts": []
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_lemmatize_success(client, mock_model):
    """Test lemmatize endpoint with valid request."""
    response = client.post(
        "/lemmatize",
        json={
            "model": "test_model",
            "texts": ["Hello world", "Testing lemmatization"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Check structure
    assert "annotations" in data
    assert "tokens" in data
    assert "model" in data
    assert "processing_time_ms" in data
    
    # Check content
    assert data["model"] == "test_model"
    assert isinstance(data["annotations"], list)
    assert isinstance(data["tokens"], list)
    assert len(data["tokens"]) == 2  # Two texts
    
    # Check default fields
    assert "text" in data["annotations"]
    assert "lemma" in data["annotations"]
    assert "pos" in data["annotations"]
    
    # Check token structure
    first_doc = data["tokens"][0]
    assert isinstance(first_doc, list)
    assert len(first_doc) == 2  # Two words in "Hello world"
    
    first_token = first_doc[0]
    assert isinstance(first_token, list)
    assert len(first_token) == len(data["annotations"])


def test_lemmatize_custom_fields(client, mock_model):
    """Test lemmatize endpoint with custom fields."""
    response = client.post(
        "/lemmatize",
        json={
            "model": "test_model",
            "texts": ["Hello world"],
            "fields": ["text", "lemma"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Check only requested fields
    assert data["annotations"] == ["text", "lemma"]
    assert len(data["tokens"][0][0]) == 2


def test_lemmatize_invalid_fields(client, mock_model):
    """Test lemmatize endpoint with invalid fields."""
    response = client.post(
        "/lemmatize",
        json={
            "model": "test_model",
            "texts": ["Hello world"],
            "fields": ["text", "invalid_field"]
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert "invalid_field" in data["error"]

