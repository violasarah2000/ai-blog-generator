"""
Model backend initialization and factory.

Centralizes backend selection logic based on configuration.
"""

import logging
from typing import Dict, Any
from app.model_backend import create_backend, ModelBackend

logger = logging.getLogger(__name__)


def init_model_backend(config: Dict[str, Any]) -> ModelBackend:
    """
    Initialize and return Ollama model backend.

    Uses Ollama for local LLM serving.

    Args:
        config: Configuration dictionary with backend-specific settings:
                - OLLAMA_BASE_URL: Ollama server URL (default: http://localhost:11434)
                - OLLAMA_MODEL: Model name in Ollama (default: stablelm-zephyr:3b)

    Returns:
        Initialized OllamaBackend instance

    Raises:
        RuntimeError: If Ollama connection fails
    """
    logger.info("Initializing model backend: OLLAMA")

    try:
        backend = create_backend(
            "ollama",
            ollama_base_url=config.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=config.get("OLLAMA_MODEL", "stablelm-zephyr:3b"),
        )
        logger.info("✓ Model backend initialized successfully.")
        return backend

    except Exception as e:
        logger.exception("Fatal error: Failed to initialize Ollama backend.")
        raise RuntimeError(f"Could not initialize Ollama backend: {e}")
