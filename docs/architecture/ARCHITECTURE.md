# System Architecture

## Overview

The AI Blog Generator is a secure, production-ready Flask application that demonstrates modern AI security practices. It supports multiple model backends and includes comprehensive security controls.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client/Load Balancer                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask Application                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Request Handler (ai_blog_generator.py)                   │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Input Validation                                     │ │ │
│  │  │ - HTML/XSS Sanitization (Bleach)                    │ │ │
│  │  │ - Topic length validation                           │ │ │
│  │  │ - Type checking                                      │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                      ▼                                      │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Rate Limiting (Flask-Limiter)                       │ │ │
│  │  │ - 10 req/min per IP                                 │ │ │
│  │  │ - 100 req/hour per IP                               │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                      ▼                                      │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Model Backend (model_backend.py)                    │ │ │
│  │  │ ┌────────────────────────────────────────────────┐  │ │
│  │  │ │ OllamaBackend       HuggingFaceBackend       │  │ │
│  │  │ │ (HTTP API)          (transformers library)    │  │ │
│  │  │ └────────────────────────────────────────────────┘  │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                      ▼                                      │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Output Processing                                   │ │ │
│  │  │ - Prompt echoing removal                            │ │ │
│  │  │ - URL injection prevention                          │ │ │
│  │  │ - Content filtering                                 │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                      ▼                                      │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Response Handler (JSON)                             │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Security Headers (Flask-Talisman)                         │ │
│  │ - Content-Security-Policy                                 │ │
│  │ - X-Content-Type-Options                                  │ │
│  │ - X-Frame-Options                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                  ▼
   ┌─────────────┐                   ┌──────────────────┐
   │   Ollama    │                   │  HuggingFace     │
   │   Service   │                   │  Models (local)  │
   │             │                   │                  │
   │ stablelm    │                   │ stabilityai/     │
   │ -zephyr-3b  │                   │ stablelm-zephyr- │
   │             │                   │ 3b               │
   └─────────────┘                   └──────────────────┘
```

---

## Components

### 1. **Flask Application** (`app/main.py`)

Main web application factory and request handlers.

**Endpoints:**
- `POST /generate` - Generate blog post from topic (rate limited: 10 req/min)
- `POST /debug_tokens` - Debug token counting
- `GET /status` - Health check (rate limit exempt)

**Features:**
- Flask factory pattern for app initialization
- Flask-Talisman for HTTPS security headers
- Flask-Limiter for rate limiting
- Configurable via `config.py`
- Centralized error handling

### 2. **Input Validation** (`app/validators.py`)

Centralized validation and sanitization layer.

**Classes:**
- `InputValidator` - Static methods for validation
  - `validate_topic(topic: str)` - Validates topic length, characters
  - `sanitize_output(prompt, content)` - Cleans HTML/XSS with bleach

**Features:**
- Regex-based topic validation (alphanumeric + spaces only, 50-200 chars)
- Bleach HTML sanitization (strips dangerous tags)
- Type hints and comprehensive error messages
- Testable, reusable validation logic

### 3. **Generation Service** (`app/generation.py`)

Business logic for content generation with retry strategy.

**Classes:**
- `GenerationService` - Coordinates generation process
  - `generate_with_retry(prompt, gen_kwargs)` - Generate with 3 retries
  - `get_token_count(text)` - Delegate to backend

**Features:**
- Automatic retry logic (3 attempts max)
- Exponential backoff on failures
- Comprehensive error logging
- Backend abstraction

### 4. **Model Backend Abstraction** (`app/model_backend.py` + `app/backends.py`)

Plugin architecture supporting multiple model providers.

**Base Class:** `ModelBackend` (abstract)
- `generate(prompt, **kwargs)` - Generate text
- `get_token_count(text)` - Count tokens

**Implementations:**

#### OllamaBackend
- **Connection**: HTTP requests to Ollama API
- **URL**: `http://localhost:11434` (configurable)
- **Model**: `stablelm-zephyr:3b` (configurable)
- **Features**: 
  - Connection verification on initialization
  - Model availability checking
  - Timeout protection (300 seconds)
  - Token estimation via embeddings endpoint
  - Comprehensive error logging

#### HuggingFaceBackend
- **Connection**: Direct Python transformers library
- **Model**: `stabilityai/stablelm-zephyr-3b` (configurable)
- **Features**:
  - GPU/CPU auto-detection
  - Pipeline-based generation
  - Accurate token counting via tokenizer
  - Device mapping for optimal memory usage

**Factory Function:** `init_model_backend(config)` (`app/backends.py`)
- Routes to correct backend based on `MODEL_BACKEND` config
- Handles initialization errors gracefully

---

## Data Flow

### Blog Generation Request

```
1. Client sends POST /generate
   ├─ JSON payload: {"topic": "..."}
   └─ Headers: Content-Type: application/json

2. Request Handler
   ├─ Extract JSON body
   ├─ Validate topic (bleach.clean, length check)
   └─ Check rate limit

3. Prompt Construction
   └─ Build system prompt with topic

4. Model Backend Selection
   ├─ If MODEL_BACKEND=ollama
   │  └─ OllamaBackend.generate() → HTTP POST to Ollama API
   └─ If MODEL_BACKEND=huggingface
      └─ HuggingFaceBackend.generate() → transformers pipeline

5. Generation Process
   ├─ Set parameters (temp, top_p, max_tokens)
   ├─ Call model
   └─ Retry on empty/echo output

6. Output Processing
   ├─ Remove prompt echo
   ├─ Prevent URL injection (linkify=None)
   └─ Clean malicious content

7. Response
   └─ JSON: {topic, content, gen_seconds}
```

---

## Configuration Management

### Environment Variables

Loaded via `.env` file:

```env
# Model Backend
MODEL_BACKEND=ollama|huggingface
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=stablelm-zephyr-3b
HUGGINGFACE_MODEL_NAME=stabilityai/stablelm-zephyr-3b

# Generation
MAX_NEW_TOKENS=500
GEN_TEMPERATURE=0.7
GEN_TOP_P=0.9

# Security
MAX_TOPIC_LEN=200
RATE_LIMIT_HOURLY=100
RATE_LIMIT_MINUTELY=10

# Flask
FLASK_ENV=development|production
DEBUG=True|False
```

### Configuration Validation

On startup, `Config.validate()` checks:
- Valid `MODEL_BACKEND` value
- Required backend configuration
- Model availability (connection test)

---

## Deployment Models

### Local Development (Ollama)

```
Your Machine
├── Flask App (port 5000)
├── Ollama Service (port 11434)
└── Model (stablelm-zephyr-3b)
```

**Setup:**
```bash
ollama serve &
python ai_blog_generator.py
```

### Local Development (HuggingFace)

```
Your Machine
├── Flask App (port 5000)
└── Model (loaded in process)
```

**Setup:**
```bash
python ai_blog_generator.py
```

### Production (Docker + Ollama)

```
Docker Network
├── Flask Container (port 5000)
└── Ollama Container (port 11434)
```

**See**: [DEPLOYMENT.md](../guides/DEPLOYMENT.md)

### Production (Kubernetes)

```
Kubernetes Cluster
├── Flask Deployment (3 replicas)
├── Ollama StatefulSet (1 replica)
└── Ingress Controller
```

**See**: [DEPLOYMENT.md](../guides/DEPLOYMENT.md)

---

## Security Architecture

### Threat Mitigation

| Threat | Layer | Mitigation |
|--------|-------|-----------|
| **Prompt Injection** | Model | Instruction-tuned model, guardrails |
| | App | Input validation, output filtering |
| | Process | Rate limiting, timeout protection |
| **XSS/HTML Injection** | Input | Bleach sanitization |
| | Output | HTML entity encoding, linkify disabled |
| | Headers | CSP, X-Content-Type-Options |
| **DoS** | Network | Rate limiting, load balancer |
| | App | Timeout (120s), connection pooling |
| | Model | Token limits, retry logic |
| **Dependency Vulnerabilities** | CI/CD | pip-audit weekly scans |
| | SBOM | CycloneDX tracking |
| | Pinning | All versions locked |

### Defense in Depth

1. **Network Layer** - Load balancer, rate limiting
2. **Application Layer** - Input validation, output filtering
3. **Model Layer** - Guardrails, token limits
4. **Process Layer** - Timeout protection, error handling
5. **Dependency Layer** - Version pinning, vulnerability scanning

---

## Performance Considerations

### Generation Performance

| Backend | CPU | Memory | Startup | Per-Request |
|---------|-----|--------|---------|------------|
| **Ollama** | ✓ Good | ✓ Low | Fast | ~8-15s |
| **HuggingFace** | ✓ Better | ⚠ High | Slow | ~8-15s |

### Scaling Recommendations

- **<100 RPS**: Single instance sufficient
- **100-1000 RPS**: Load balancer + 3-5 instances
- **>1000 RPS**: Multi-region, CDN, caching layer

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Web Framework** | Flask | 2.3.3 | REST API, request routing |
| **Security** | Flask-Talisman | 1.1.0 | HTTPS headers, CSP |
| | Flask-Limiter | 2.9.2 | Rate limiting (10 req/min) |
| | Bleach | 6.3.0 | HTML sanitization, XSS prevention |
| **ML Backends** | transformers | 4.53.0 | HuggingFace model loading (RCE fixes) |
| | torch | 2.2.2 | PyTorch ML framework |
| | huggingface-hub | ≥0.22.0 | Model downloading |
| | accelerate | ≥0.29.0 | GPU acceleration |
| **Server** | Gunicorn | 23.0.0 | WSGI application server |
| **HTTP** | requests | 2.32.5 | Ollama API client |
| **Config** | python-dotenv | ≥1.0.0 | Environment variable loading |
| **Testing** | pytest | 8.0+ | Unit/integration testing |
| **CI/CD** | GitHub Actions | - | Automated testing & scanning |
| **Containerization** | Docker | - | Production deployment |

---

## Security Infrastructure

### Testing & Validation

**Fuzz Testing Framework** (`security/fuzzing/framework.py`)
- 100+ prompt injection payloads
- 30+ long input attack vectors
- 20+ unicode/encoding attacks
- 50+ rate limiting tests
- Auto-generated HTML + JSON reports
- Runs in CI/CD on every commit

**Red Team Testing** (`security/red_team/`)
- MITRE ATLAS framework tactics
- Known jailbreak techniques
- LLM-specific adversarial examples
- Attack payload corpus
- Results tracking (redteam_results.json)

**Vulnerability Scanning**
- CodeQL (GitHub) - 0 issues
- pip-audit - 0 CVEs
- safety - 0 issues
- Scheduled weekly + per-commit

**Threat Modeling**
- STRIDE analysis
- PASTA risk methodology
- 18 specific threats identified
- Mitigations documented
- See: `security/threat_model/threat_model.md`

### Documentation & Compliance

**Cryptographic Bill of Materials** (`security/supply_chain/CBOM.md`)
- Active components: TLS 1.2/1.3, HMAC-SHA1
- Proposed components: JWT, AES-GCM, GPG signing
- Implementation roadmap
- Compliance mapping (NIST, CycloneDX)

**Software Bill of Materials** (`security/supply_chain/sbom.json`)
- CycloneDX 1.4 format
- 11 core dependencies tracked
- Package URLs (PURLs) included
- Regular updates on new releases

**Security Policies** (`docs/security/SECURITY.md`)
- Vulnerability reporting procedures
- Responsible disclosure policy
- Security testing documentation
- Compliance references

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST Secure SDLC](https://csrc.nist.gov/publications/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [CycloneDX SBOM Standard](https://cyclonedx.org/)
- [STRIDE Threat Modeling](https://en.wikipedia.org/wiki/STRIDE_(security))
