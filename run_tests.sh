#!/usr/bin/env zsh
# Run unit tests only (fast, uses mocks)
echo "Running unit tests (no Ollama required)..."
pytest tests/ --ignore=tests/integration/ -v -q

echo ""
echo "========================================"
echo ""

# Run integration tests (slow, requires live Ollama)
echo "Running integration tests (requires live Ollama)..."
pytest tests/integration/ -v --tb=short
