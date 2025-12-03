"""Configuration management for AI Blog Generator.
Uses Ollama for local LLM serving.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""

    # Ollama Configuration (local model serving)
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "stablelm-zephyr:3b")

    # Generation Parameters
    MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", 500))
    GEN_TEMPERATURE = float(os.environ.get("GEN_TEMPERATURE", 0.7))
    GEN_TOP_P = float(os.environ.get("GEN_TOP_P", 0.9))
    MAX_TOPIC_LEN = int(os.environ.get("MAX_TOPIC_LEN", 200))

    # Rate Limiting
    RATE_LIMIT_HOURLY = int(os.environ.get("RATE_LIMIT_HOURLY", 100))
    RATE_LIMIT_MINUTELY = int(os.environ.get("RATE_LIMIT_MINUTELY", 10))

    # Flask Configuration
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")

    @classmethod
    def validate(cls):
        """Validate configuration and provide helpful error messages."""
        print(
            f"✓ Using Ollama backend: {cls.OLLAMA_MODEL} @ {cls.OLLAMA_BASE_URL}"
        )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    FLASK_ENV = "production"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    FLASK_ENV = "testing"
