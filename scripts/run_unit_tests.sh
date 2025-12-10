#!/bin/bash
# Unit Tests - Fast test suite with mocked backends
# Usage: ./scripts/run_unit_tests.sh

set -e

echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo "🧪 Running unit tests with coverage..."
pytest tests/ --ignore=tests/integration/ -v --cov=app --cov=security/fuzzing --cov-report=xml

echo "✅ Unit tests passed!"
