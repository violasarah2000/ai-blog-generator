"""Pytest configuration for integration tests (uses live backends)."""

import pytest
import os
import requests
from unittest.mock import patch
from app import create_app
from app.config import TestingConfig


def get_available_ollama_model():
    """Detect what Ollama models are available and return a suitable one."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        
        if not models:
            raise RuntimeError("No models available in Ollama")
        
        # Get exact model names
        model_names = [m.get("name", "") for m in models]
        
        # Filter out embedding models, get text generation models
        text_models = [m for m in model_names if "embed" not in m.lower()]
        
        if not text_models:
            text_models = model_names
        
        return text_models[0]
    except Exception as e:
        raise RuntimeError(
            f"Could not detect Ollama models. Is Ollama running at localhost:11434? Error: {e}"
        )


@pytest.fixture
def app():
    """Create app for integration testing with LIVE Ollama backend."""
    # Detect available model
    available_model = get_available_ollama_model()
    
    # Create app and patch its model backend configuration
    with patch.object(TestingConfig, 'OLLAMA_MODEL', available_model):
        app = create_app(TestingConfig)
    
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner for testing commands."""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """Create application context for testing."""
    with app.app_context():
        yield app


def pytest_configure(config):
    """Add markers for integration tests."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (requires Ollama running)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark all tests in this directory as integration tests."""
    for item in items:
        item.add_marker(pytest.mark.integration)
        item.add_marker(pytest.mark.slow)
