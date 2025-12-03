# Build Artifacts

This directory contains build and deployment configurations.

## Contents

- **Dockerfile** - Production Docker image configuration
- **docker-compose.yml** - (coming soon) Multi-service orchestration
- **.dockerignore** - (coming soon) Build context optimization

## Building

### Docker Build

```bash
# Build the production image
docker build -f build/Dockerfile -t ai-blog-generator:latest .

# Run the container
docker run -p 5000:5000 ai-blog-generator:latest
```

### With Environment Variables

```bash
docker run -p 5000:5000 \
  -e MODEL_BACKEND=ollama \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  ai-blog-generator:latest
```

## Production Notes

- Uses Gunicorn as WSGI server
- Requires Python 3.11+
- GPU support: Add `--gpus all` to docker run for CUDA models
