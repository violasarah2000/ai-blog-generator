"""Model backends for AI Blog Generator.
Supports Ollama API for local LLM serving.
"""

import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ModelBackend(ABC):
    """Abstract base class for model backends."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Count tokens in text."""
        pass


class OllamaBackend(ModelBackend):
    """Ollama API backend for local LLM serving."""

    def __init__(self, base_url: str, model_name: str):
        """
        Initialize Ollama backend.

        Args:
            base_url: Ollama server URL (e.g., http://localhost:11434)
            model_name: Model name as registered in Ollama (e.g., stablelm-zephyr-3b)
        """
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.generate_url = f"{self.base_url}/api/generate"
        self.embeddings_url = f"{self.base_url}/api/embeddings"

        # Verify Ollama is running
        self._verify_connection()

    def _verify_connection(self):
        """Verify connection to Ollama server."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]

            if self.model_name not in model_names:
                logger.warning(
                    f"Model '{self.model_name}' not found in Ollama. "
                    f"Available models: {model_names}"
                )
            else:
                logger.info(f"✓ Connected to Ollama. Model '{self.model_name}' available.")
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Ollama at {self.base_url}. "
                f"Ensure Ollama is running: ollama serve\nError: {e}"
            )

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama API."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "num_predict": kwargs.get("max_new_tokens", 500),
            },
        }

        try:
            response = requests.post(self.generate_url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"Model generation failed: {e}")

    def get_token_count(self, text: str) -> int:
        """Get token count using Ollama embeddings endpoint."""
        try:
            response = requests.post(
                self.embeddings_url,
                json={"model": self.model_name, "prompt": text},
                timeout=30,
            )
            response.raise_for_status()
            # Ollama doesn't directly return token count, estimate from embedding dimension
            result = response.json()
            embedding = result.get("embedding", [])
            # Rough heuristic: tokens ≈ characters / 4
            return max(1, len(text) // 4)
        except Exception:
            # Fallback estimation
            return len(text) // 4



def create_backend(backend_type: str, **config) -> ModelBackend:
    """
    Factory function to create Ollama model backend.

    Args:
        backend_type: "ollama"
        **config: Backend-specific configuration

    Returns:
        OllamaBackend instance
    """
    backend_type = backend_type.lower()

    if backend_type == "ollama":
        return OllamaBackend(
            base_url=config.get("ollama_base_url", "http://localhost:11434"),
            model_name=config.get("ollama_model", "stablelm-zephyr:3b"),
        )
    else:
        raise ValueError(f"Only 'ollama' backend is supported. Got: {backend_type}")
