"""
AI Blog Generator application package.

This package contains the core Flask application for generating blog posts
using secure LLM backends (Ollama or HuggingFace).
"""

from app.main import create_app

__version__ = "1.0.0"
__author__ = "SperksWerks LLC"

__all__ = ["create_app"]
