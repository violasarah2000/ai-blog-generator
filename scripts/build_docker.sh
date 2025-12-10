#!/bin/bash
# Docker Build - Build production Docker image
# Usage: ./scripts/build_docker.sh [tag]

set -e

TAG=${1:-"latest"}

echo "🐳 Building Docker image: blog-generator:${TAG}"
docker build -f config/docker/Dockerfile -t blog-generator:${TAG} .

echo "✅ Docker image built successfully!"
echo "   Image: blog-generator:${TAG}"
echo "   Run with: docker run -p 5000:5000 blog-generator:${TAG}"
