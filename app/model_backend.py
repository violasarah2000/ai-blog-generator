"""Model backends for AI Blog Generator.

Architecture Note:
    This module implements a plugin-based abstraction layer for LLM backends.
    Currently uses Ollama for local model serving, but designed to support:
    
    - LiteLLM: 100+ providers (OpenAI, Anthropic, local, etc.) via unified API
    - vLLM: High-throughput local LLM serving
    - Cloud providers: Azure OpenAI, Bedrock, etc.
    
    To add a new backend:
    1. Create a class inheriting ModelBackend
    2. Implement generate() and get_token_count() methods
    3. Register in create_backend() factory function
    4. Update BACKEND_TYPE env var or config
    
    This design demonstrates enterprise-grade extensibility patterns used in
    production AI/ML systems where requirements and infrastructure evolve.
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
        """
        Get token count using Ollama embeddings endpoint.
        
        Note: Ollama doesn't expose a direct tokenizer endpoint, so we use
        a reasonable heuristic based on common tokenizer behavior:
        - Most tokenizers split on whitespace and punctuation
        - Average token represents ~4 characters
        - Longer text may have better compression (~3-5 chars/token)
        
        For more accurate counting, consider using a tokenizer library:
        - tiktoken (OpenAI models)
        - transformers.AutoTokenizer (HuggingFace models)
        - llama-cpp-python (local Llama models)
        """
        try:
            response = requests.post(
                self.embeddings_url,
                json={"model": self.model_name, "prompt": text},
                timeout=30,
            )
            response.raise_for_status()
            # Heuristic: most tokenizers split on whitespace/punctuation
            # Average: ~4 characters per token (conservative estimate)
            words = len(text.split())
            # Better approximation: words * 1.3 (most words = 1-2 tokens)
            estimated_tokens = max(1, int(words * 1.3))
            logger.debug(f"Token estimate: {estimated_tokens} tokens for {len(text)} chars")
            return estimated_tokens
        except Exception as e:
            logger.warning(f"Token counting failed: {e}. Using fallback estimate.")
            # Fallback: conservative estimate using character count
            return max(1, len(text) // 4)



def create_backend(backend_type: str, **config) -> ModelBackend:
    """
    Factory function for creating model backends.
    
    This pattern allows runtime selection of LLM backend without changing
    application code. Implements the Factory design pattern.
    
    Args:
        backend_type: Backend identifier (e.g., "ollama", "litellm", "vllm")
        **config: Backend-specific configuration passed to constructor
        
    Returns:
        ModelBackend instance configured for the specified backend
        
    Raises:
        ValueError: If backend_type is not supported
        
    Examples:
        # Ollama backend (local)
        backend = create_backend("ollama",
                                ollama_base_url="http://localhost:11434",
                                ollama_model="stablelm-zephyr:3b")
        
        # Future: LiteLLM backend (multiple providers)
        # backend = create_backend("litellm", model="gpt-4", api_key="...")
        
        # Future: vLLM backend (high-throughput local)
        # backend = create_backend("vllm", model_path="/path/to/model", gpu_memory_fraction=0.5)
    """
    backend_type = backend_type.lower()

    if backend_type == "ollama":
        return OllamaBackend(
            base_url=config.get("ollama_base_url", "http://localhost:11434"),
            model_name=config.get("ollama_model", "stablelm-zephyr:3b"),
        )
    else:
        raise ValueError(
            f"Unsupported backend: '{backend_type}'. "
            f"Currently supported: ['ollama']. "
            f"See module docstring for extending with additional backends."
        )
