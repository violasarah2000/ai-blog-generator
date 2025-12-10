#!/usr/bin/env python3
"""
Entry point for AI Blog Generator.

Usage:
    python run.py
    
This script initializes the Flask app and runs it on localhost:5000
"""

from app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
