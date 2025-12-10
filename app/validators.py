"""Centralized input validation and output sanitization."""

import bleach
from app.config import Config


class ValidationError(ValueError):
    """Raised when validation fails."""
    pass


class InputValidator:
    """Centralized input validation for blog generator."""
    
    @staticmethod
    def validate_topic(topic: str) -> str:
        """
        Validate and normalize topic string.
        
        Args:
            topic: The topic to validate
            
        Returns:
            The normalized topic string
            
        Raises:
            ValidationError: If topic is invalid
        """
        if not topic or not isinstance(topic, str):
            raise ValidationError("Topic must be a non-empty string")
        
        # Check if topic is only whitespace
        if not topic.strip():
            raise ValidationError("Topic cannot be empty or whitespace-only")
        
        # Check length
        if len(topic) > Config.MAX_TOPIC_LEN:
            raise ValidationError(
                f"Topic exceeds maximum length of {Config.MAX_TOPIC_LEN} characters"
            )
        
        # Use bleach to strip any dangerous tags/attributes
        cleaned = bleach.clean(topic, strip=True)
        if cleaned != topic:
            raise ValidationError("Topic contains HTML/markup which is not allowed")
        
        return topic.strip()
    
    @staticmethod
    def sanitize_output(prompt: str, content: str) -> str:
        """
        Remove echoed prompt and dangerous content from model output.
        
        Args:
            prompt: The original prompt that was sent to the model
            content: The model's generated response
            
        Returns:
            Sanitized output with prompt removed and URLs stripped
        """
        if not content:
            return ""
        
        # Remove echoed prompt
        result = content.replace(prompt, "").strip()
        
        # Strip URLs using bleach
        result = bleach.linkify(result, callbacks=[lambda attrs, new: None])
        
        return result.strip()
