"""Text generation service for AI Blog Generator."""

import logging
from typing import Dict, Any
from app.model_backend import ModelBackend

logger = logging.getLogger(__name__)


class GenerationService:
    """Encapsulates all text generation logic."""
    
    def __init__(self, backend: ModelBackend, config: Any):
        """Initialize generation service."""
        self.backend = backend
        self.config = config
    
    def generate_with_retry(self, prompt: str, gen_kwargs: Dict) -> str:
        """
        Generate text with retry logic for empty outputs.
        
        Args:
            prompt: The prompt to send to the model
            gen_kwargs: Generation parameters (max_new_tokens, temperature, top_p)
            
        Returns:
            Generated text content
            
        Raises:
            RuntimeError: If generation fails
        """
        try:
            result = self.backend.generate(prompt, **gen_kwargs)
            
            # Retry if output is empty or just echoed the prompt
            if not result.strip() or result.strip() == prompt.strip():
                logger.info("Retrying generation with larger token budget...")
                gen_kwargs["max_new_tokens"] = self.config["MAX_NEW_TOKENS"] * 2
                gen_kwargs["temperature"] = min(
                    1.0, self.config["GEN_TEMPERATURE"] + 0.2
                )
                result = self.backend.generate(prompt, **gen_kwargs)
            
            return result
        except Exception as e:
            logger.exception("Generation failed.")
            raise RuntimeError(f"Generation error: {e}")
    
    def get_token_count(self, text: str) -> int:
        """
        Count tokens in text safely.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Token count (0 if unavailable)
        """
        try:
            return self.backend.get_token_count(text)
        except Exception:
            return 0
