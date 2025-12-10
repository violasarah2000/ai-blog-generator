#!/bin/bash
# Security Scanning - Dependency vulnerability scanning
# Usage: ./scripts/run_security_scan.sh

set -e

echo "🔒 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install safety pip-audit

echo "🔍 Running Safety vulnerability scan..."
safety check --json > safety-report.json || true
cat safety-report.json

echo "🔍 Running pip-audit vulnerability scan..."
pip-audit --desc --format json > pip-audit-report.json || true
cat pip-audit-report.json

echo "✅ Running final vulnerability check..."
safety check

echo "✅ Security scans completed!"
