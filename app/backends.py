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
    Initialize and return model backend based on configuration.

    Centralizes backend selection logic to avoid duplication between
    app initialization and direct calls.

    Args:
        config: Configuration dictionary with MODEL_BACKEND and backend-specific settings:
                - MODEL_BACKEND: "ollama" or "huggingface"
                - OLLAMA_BASE_URL: Ollama server URL (if using ollama)
                - OLLAMA_MODEL: Model name in Ollama (if using ollama)
                - HUGGINGFACE_MODEL_NAME: HuggingFace model ID (if using huggingface)

    Returns:
        Initialized ModelBackend instance

    Raises:
        ValueError: If backend type is unknown
        RuntimeError: If backend initialization fails
    """
    backend_type = config.get("MODEL_BACKEND", "ollama").lower()

    logger.info(f"Initializing model backend: {backend_type.upper()}")

    try:
        if backend_type == "ollama":
            backend = create_backend(
                "ollama",
                ollama_base_url=config.get("OLLAMA_BASE_URL", "http://localhost:11434"),
                ollama_model=config.get("OLLAMA_MODEL", "stablelm-zephyr:3b"),
            )
        elif backend_type == "huggingface":
            backend = create_backend(
                "huggingface",
                model_name=config.get("HUGGINGFACE_MODEL_NAME", "stabilityai/stablelm-zephyr-3b"),
            )
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")

        logger.info("✓ Model backend initialized successfully.")
        return backend

    except Exception as e:
        logger.exception("Fatal error: Failed to initialize model backend.")
        raise RuntimeError(f"Could not initialize model backend: {e}")
