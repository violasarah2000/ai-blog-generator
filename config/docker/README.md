# Docker Configuration

This directory contains all Docker-related configuration and deployment files for the blog-content-engine.

## Contents

- **Dockerfile** - Multi-stage production image (optimized, non-root user, health checks)
- **docker-compose.yml** - Multi-service orchestration (app + Ollama)
- **.dockerignore** - Build context optimization
- **DEPLOYMENT.md** - Complete deployment guide

## Quick Start

### Build Locally

```bash
# Build the production image
docker build -f config/docker/Dockerfile -t blog-generator:latest .

# Run the container
docker run -p 5000:5000 blog-generator:latest
```

### With Docker Compose (Recommended)

```bash
# Start app + Ollama together
docker-compose -f config/docker/docker-compose.yml up -d

# View logs
docker-compose -f config/docker/docker-compose.yml logs -f app

# Stop services
docker-compose -f config/docker/docker-compose.yml down
```

## Environment Variables

The container reads from `.env`:

```bash
MODEL_BACKEND=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=neural-chat
MAX_NEW_TOKENS=500
```

## Production Notes

- **Multi-stage build**: Reduces image size by ~60% (build tools not included)
- **Non-root user**: Runs as `appuser` (UID 1000) for security
- **Health checks**: Automated monitoring of container health
- **Gunicorn**: Production WSGI server with 4 workers
- **Python 3.11-slim**: Minimal base image

## Full Documentation

👉 See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for:
- Advanced configuration
- GPU support (CUDA models)
- Scaling strategies
- Troubleshooting
- Security best practices

## Architecture

The Dockerfile uses a two-stage build:

1. **Builder stage**: Installs dependencies with build tools
2. **Runtime stage**: Minimal image with only runtime dependencies

This approach reduces attack surface and image size.
