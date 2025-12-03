#!/bin/bash
# Code Quality Checks - Linting, formatting, type checking
# Usage: ./scripts/run_code_quality.sh

set -e

echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

echo "🎨 Checking code formatting with black..."
black app/ security/fuzzing/ tests/ --check

echo "📋 Checking import sorting with isort..."
isort app/ security/fuzzing/ tests/ --check-only

echo "🔍 Linting with flake8..."
flake8 app/ security/fuzzing/ tests/ --max-line-length=100 --exclude=__pycache__,venv

echo "🔬 Type checking with mypy..."
mypy app/ security/fuzzing/ --ignore-missing-imports

echo "✅ All code quality checks passed!"
