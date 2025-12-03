# 🐳 Docker & Deployment Guide

## Quick Start with Docker Compose

The easiest way to run the AI Blog Generator with all dependencies:

```bash
# Clone the repository
git clone <repo-url>
cd blog-content-engine

# Start services (includes app + Ollama)
docker-compose -f config/docker/docker-compose.yml up -d

# Initialize Ollama with a model (first time only)
docker exec blog-generator-ollama ollama pull stablelm-zephyr:3b

# Check service status
docker-compose -f config/docker/docker-compose.yml ps

# View logs
docker-compose -f config/docker/docker-compose.yml logs -f app
docker-compose -f config/docker/docker-compose.yml logs -f ollama

# Stop services
docker-compose -f config/docker/docker-compose.yml down
```

**App will be available at**: http://localhost:5000

---

## Building Docker Image Manually

```bash
# Build the image
docker build -f config/docker/Dockerfile -t blog-generator:latest .

# Run the container
docker run -d \
  --name blog-generator \
  -p 5000:5000 \
  -e MODEL_BACKEND=ollama \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  blog-generator:latest

# View logs
docker logs -f blog-generator

# Stop container
docker stop blog-generator
```

---

## Multi-Stage Build Explanation

The `Dockerfile` uses a two-stage build to minimize image size:

### Stage 1: Builder
- Installs build dependencies (gcc, make, etc.)
- Compiles Python packages with C extensions
- Keeps build tools out of final image

### Stage 2: Runtime
- Copies only compiled dependencies from builder
- No build tools included (smaller image)
- Runs as non-root user `appuser` (security)

**Result**: ~500MB production image (vs 1GB+ if build tools included)

---

## Docker Compose Services

### Flask Application Service
- **Port**: 5000
- **Health Check**: `/status` endpoint every 30s
- **Depends On**: Ollama service (waits for it to be healthy)
- **Volumes**: `./logs` for application logs
- **Environment Variables**: Configure via `.env` file

### Ollama Service  
- **Port**: 11434
- **Model Storage**: Docker volume `ollama_data` (persistent)
- **Health Check**: `/api/tags` endpoint every 30s
- **First Run**: Pull model with `docker exec` command

---

## Configuration

### Environment Variables

Create a `.env` file in project root:

```bash
# Flask Configuration
FLASK_ENV=production
DEBUG=False

# Model Backend
MODEL_BACKEND=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=stablelm-zephyr:3b

# Generation Settings
MAX_TOPIC_LEN=200
MAX_NEW_TOKENS=500

# Rate Limiting
RATE_LIMIT_MINUTELY=10
RATE_LIMIT_HOURLY=100

# HuggingFace (if using HF backend)
HF_TOKEN=your_token_here
HF_MODEL=stabilityai/stablelm-zephyr-3b
```

### Using External Ollama

If Ollama is running separately (not in Docker):

```bash
docker run -d \
  --name blog-generator \
  -p 5000:5000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  blog-generator:latest
```

Replace `host.docker.internal` with your Ollama server IP for network access.

---

## Container Networking

### Docker Compose Network
- Service name `ollama` = DNS hostname inside container
- Containers communicate via internal `blog-network`
- Port 11434 only exposed to host if accessed from outside

### Port Mapping
- `5000:5000` - Flask app (host:container)
- `11434:11434` - Ollama (host:container)

---

## Volumes & Persistence

### Application Logs
- `./logs:/app/logs` - Bind mount from host
- Logs persist after container stops

### Ollama Model Data
- `ollama_data:/root/.ollama` - Named Docker volume
- Models persist across restarts
- Can backup with: `docker run --rm -v ollama_data:/data -v $(pwd):/backup ubuntu tar czf /backup/ollama_backup.tar.gz -C /data .`

---

## Troubleshooting

### App can't connect to Ollama
```bash
# Check if Ollama is running
docker-compose -f config/docker/docker-compose.yml ps

# Check Ollama logs
docker-compose -f config/docker/docker-compose.yml logs ollama

# Test connection
docker exec blog-generator-app curl http://ollama:11434/api/tags
```

### Port already in use
```bash
# Check what's using port 5000
lsof -i :5000

# Use different port
docker run -p 8080:5000 ...

# Or change docker-compose.yml ports section
```

### Model not found
```bash
# Pull the model first
docker exec blog-generator-ollama ollama pull stablelm-zephyr:3b

# List available models
docker exec blog-generator-ollama ollama list
```

### Out of disk space
```bash
# Check Docker disk usage
docker system df

# Clean up unused images/volumes
docker system prune -a --volumes
```

### Container keeps restarting
```bash
# Check health status
docker-compose -f config/docker/docker-compose.yml ps

# View detailed logs
docker-compose -f config/docker/docker-compose.yml logs app --tail 100
```

---

## Production Deployment

### Pre-Deployment Checklist
- ✅ All tests passing: `pytest tests/`
- ✅ Security scans clean: `python scripts/security_scan.py`
- ✅ Docker image builds: `docker build -f config/docker/Dockerfile .`
- ✅ Health checks respond: `curl http://localhost:5000/status`

### Scaling Options

**Docker Swarm:**
```bash
docker swarm init
docker stack deploy -c config/docker/docker-compose.yml blog-generator
```

**Kubernetes (Helm):**
Use the Dockerfile with Kubernetes deployment manifests. See `docs/k8s/` for templates.

**Cloud Platforms:**
- **AWS**: ECS with Fargate or EC2
- **GCP**: Cloud Run or GKE
- **Azure**: Container Instances or AKS

### Performance Tuning

**Gunicorn Workers**:
- Current: 4 workers
- Formula: `(2 × CPU_cores) + 1`
- Modify in `Dockerfile`: `--workers 8`

**Memory Limits**:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

**Ollama GPU Acceleration**:
```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## Monitoring & Logging

### View Logs
```bash
# Follow app logs in real-time
docker-compose -f config/docker/docker-compose.yml logs -f app

# Last 100 lines
docker-compose -f config/docker/docker-compose.yml logs app --tail 100

# All services
docker-compose -f config/docker/docker-compose.yml logs
```

### Collect Metrics
```bash
# CPU and memory usage
docker stats blog-generator-app blog-generator-ollama

# Network traffic
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.CPUPerc}}"
```

### Health Check Status
```bash
# Check health
docker inspect blog-generator-app --format='{{.State.Health.Status}}'

# Detailed health log
docker inspect blog-generator-app --format='{{json .State.Health}}'
```

---

## CI/CD Integration

See `.github/workflows/ci-cd.yml` for automated:
- Docker image building
- Security scanning
- Test execution
- Registry pushing

```yaml
# Automated on:
# - Push to main branch
# - Pull requests
# - Manual trigger (workflow_dispatch)
```

---

## File Structure

```
config/
├── docker/
│   ├── Dockerfile           # Multi-stage production image
│   ├── docker-compose.yml   # Orchestration & services
│   └── .dockerignore        # Build context exclusions
```

---

## Security Best Practices

✅ **In This Setup:**
- Non-root user (`appuser`) runs the app
- Multi-stage build eliminates build tools
- `.dockerignore` excludes sensitive files
- Health checks verify container health
- Resource limits prevent DoS

⚠️ **For Production:**
- Use secret management (AWS Secrets Manager, HashiCorp Vault)
- Scan images for vulnerabilities: `trivy image blog-generator:latest`
- Use private container registry
- Enable Docker Content Trust for signed images
- Implement network policies and firewalls
- Regular security updates for base image

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices for Python Docker Images](https://docs.docker.com/language/python/)
- [OWASP Container Security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

**Generated**: December 2, 2025  
**Last Updated**: After moving to config/docker/
