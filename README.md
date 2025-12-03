# 🧠 AI Blog Generator  
### A Secure by Design AI Engineering Demonstration Project  
Built by **SperksWerks LLC** — Showcasing Modern AI Security Testing

[![CodeQL](https://github.com/violasarah2000/ai-blog-generator/actions/workflows/codeql.yml/badge.svg)](https://github.com/violasarah2000/ai-blog-generator/actions/workflows/codeql.yml)
[![Supply Chain Security](https://github.com/violasarah2000/ai-blog-generator/actions/workflows/supply-chain-security.yml/badge.svg)](https://github.com/violasarah2000/ai-blog-generator/actions/workflows/supply-chain-security.yml)

---

## 🚀 Overview

The **AI Blog Generator** is a Python-based application that produces structured, high-quality blog content using open-source LLMs (Ollama, HuggingFace, etc.).  

But the *real* purpose of this repo? 

### 👉 To demonstrate professional **AI Security Engineering** capabilities

This project showcases the complete secure SDLC for AI systems — from traditional code security to emerging LLM-specific testing methodologies.

**You will find:**

✓ Secure Python + Flask architecture  
✓ GitHub Actions CI/CD with **SAST**, **DAST**, and **AI-focused scans**  
✓ Model safety and prompt injection testing  
✓ LLM fuzzing framework  
✓ AI red teaming tactics  
✓ STRIDE threat modeling  
✓ Secure supply chain practices (SBOM, dependency scanning)  
✓ Signed commits and protected branches  

This repository is a **portfolio demonstration** of capability in securing AI/ML pipelines for enterprise organizations.

---

## 📁 Project Structure

```
ai-blog-generator/
├── app/                          # Main application package
│   ├── __init__.py              (package init)
│   ├── main.py                  (Flask app factory)
│   ├── config.py                (configuration management)
│   └── model_backend.py         (Ollama & HuggingFace abstraction)
│
├── tests/                        # Test suite
│   ├── conftest.py              (pytest configuration)
│   ├── fixtures/                (test data)
│   ├── test_endpoints.py        (endpoint tests - ready to create)
│   └── test_security.py         (security tests - ready to create)
│
├── security/                     # Security testing frameworks
│   ├── fuzzing/                 (LLM fuzzing)
│   ├── red_team/                (adversarial attacks)
│   ├── threat_model/            (STRIDE analysis)
│   ├── guardrails/              (output filtering)
│   ├── monitoring/              (security logging)
│   ├── supply_chain/            (SBOM & hashes)
│   └── reports/                 (security documentation)
│
├── docs/                         # Complete documentation
│   ├── INDEX.md                 (navigation hub)
│   ├── guides/                  (setup, testing, deployment)
│   ├── security/                (security policy, SBOM)
│   └── architecture/            (system design)
│
├── api/                          # API documentation
│   ├── postman_collection.json  (Postman test collection)
│   └── README.md                (API guide)
│
├── config/                       # Configuration & deployment
│   ├── docker/                  (Docker configuration)
│   │   ├── Dockerfile           (production image)
│   │   ├── docker-compose.yml   (services orchestration)
│   │   ├── .dockerignore        (build exclusions)
│   │   └── DEPLOYMENT.md        (Docker guide)
│   ├── .whitesource             (dependency scanning)
│   ├── renovate.json            (dependency updates)
│   └── CODEOWNERS               (code ownership)
│
├── build/                        # Legacy build files
│   └── README.md                (older build docs)
│
├── run.py                        # Entry point for development
├── fuzz_tester.py               # LLM security fuzzer
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/violasarah2000/ai-blog-generator
cd ai-blog-generator
cp .env.example .env

# 2. Start Ollama (recommended)
ollama serve &
ollama pull stablelm-zephyr-3b

# 3. Install and run
pip install -r requirements.txt
python run.py

# 4. In another terminal, run fuzzer tests
python fuzz_tester.py
```

👉 **Full setup guide**: [docs/guides/SETUP.md](./docs/guides/SETUP.md)

---

## 🧪 Testing

This project includes **two distinct test suites**:

### Unit Tests (Fast - Use These for Development)
64 tests with mocked backends — run in ~2 seconds, no external dependencies needed.

```bash
# Run unit tests only
pytest tests/ --ignore=tests/integration/ -q

# Run specific test file
pytest tests/test_endpoints.py -v

# Run with coverage
pytest tests/ --ignore=tests/integration/ --cov=app
```

### Integration Tests (Slow - Use These Before Deployment)
10 tests using your live Ollama server — auto-detects available models, takes ~2 minutes.

```bash
# Run integration tests (requires Ollama running)
pytest tests/integration/ -v

# Run with detailed output
pytest tests/integration/ -vvs
```

### Run All Tests
```bash
# All 74 tests (unit + integration)
pytest tests/ -q

# Or use the helper script
./run_tests.sh
```

**Test Documentation**: See [tests/README_TESTS.md](./tests/README_TESTS.md) for details

---

## 🛡 Security Engineering Capabilities Demonstrated

## 1. Static Application Security Testing (SAST)
Integrated into GitHub Actions:

- CodeQL  
- Bandit  
- Semgrep (optional ruleset)  
- Dependency scanning (Dependabot/Mend)

## 2. Dynamic Application Security Testing (DAST)
The app can be scanned using:

- OWASP ZAP (API mode)
- Flask security header validation
- Local runtime checks

## 3. LLM-Specific Security Testing (core feature)

This repo includes an **AI Fuzzing Module** to test:

### ✦ Prompt Injection  
### ✦ Jailbreak Attempts  
### ✦ Response Boundary Handling  
### ✦ Refusal / Guardrail Testing  
### ✦ Context Window Attacks  
### ✦ Malicious Output Attempts (code, security bypass, etc.)  

Plus:

### ✦ AI Red Team Scripts  
Following MITRE ATLAS techniques.

---

## 📁 Security Module Structure

The `security/` folder contains comprehensive security testing and threat modeling utilities:

### `/fuzzing`
LLM-specific fuzzing framework for testing model robustness:
- **fuzz_tester.py** - Main fuzzing engine
- **fuzz_config.yaml** - Fuzzing configuration and test parameters
- **fuzz_results.md** - Results and analysis from fuzzing runs
- **fuzz_corpus/** - Test input corpora:
  - `injection_inputs.txt` - Prompt injection payloads
  - `long_prompt_inputs.txt` - Context window overflow tests
  - `unicode_inputs.txt` - Unicode/encoding attack vectors

### `/red_team`
AI red teaming attacks and adversarial testing:
- **redteam_runner.py** - Orchestrates red team attack execution
- **redteam_results.json** - Results from red team campaigns
- **mitigation_effectiveness.md** - Analysis of mitigation strategies
- **attacks/** - Curated attack database:
  - `prompt_injection.txt` - Injection attack patterns
  - `jailbreaks.txt` - Jailbreak attempts
  - `role_override.txt` - Role-based prompt manipulation
  - `context_poisoning.txt` - Context window poisoning
  - `ascii_smuggle.txt` - Character encoding bypasses

### `/threat_model`
Formal threat modeling documentation:
- **threat_model.md** - Comprehensive threat analysis
- **stride_matrix.csv** - STRIDE threat categorization
- **threat_diagram.mmd** - Mermaid threat architecture diagram

### `/guardrails`
Output filtering and policy enforcement:
- **output_filter.py** - Content filtering engine
- **sanitizer.py** - Input/output sanitization utilities
- **policies.yaml** - Security policies and rules

### `/monitoring`
Security monitoring and anomaly detection:
- **logger.py** - Centralized security logging
- **anomaly_detector.py** - Real-time anomaly detection
- **sample_logs/** - Example security event logs

### `/supply_chain`
Secure software supply chain practices:
- **sbom.json** - Software Bill of Materials
- **dependency_report.md** - Dependency security analysis
- **verify_hashes.py** - Hash verification utilities

### `/reports`
Security reports and documentation:
- **security_overview.md** - High-level security posture
- **monthly_security_report_template.md** - Recurring report template
- **portfolio_showcase.md** - Security capabilities showcase

---

## 🐳 Docker Deployment (Easiest)

The simplest way to run everything locally:

```bash
cd ai-blog-generator

# Start services (Flask app + Ollama)
docker-compose -f config/docker/docker-compose.yml up -d

# Initialize with a model (first time only)
docker exec blog-generator-ollama ollama pull stablelm-zephyr:3b

# Check services
docker-compose -f config/docker/docker-compose.yml ps

# View logs
docker-compose -f config/docker/docker-compose.yml logs -f app
```

👉 **Full deployment guide**: [config/docker/DEPLOYMENT.md](./config/docker/DEPLOYMENT.md)

---

```bash
# 1. Clone and setup
git clone https://github.com/violasarah2000/ai-blog-generator
cd ai-blog-generator
cp .env.example .env

# 2. Start Ollama (recommended)
ollama serve &
ollama pull stablelm-zephyr-3b

# 3. Install and run
pip install -r requirements.txt
python ai_blog_generator.py

# 4. In another terminal, run fuzzer tests
python fuzz_tester.py
```

👉 **Full setup guide**: [docs/guides/SETUP.md](./docs/guides/SETUP.md)

---

## 📚 Documentation

All documentation has been consolidated into a single organized location:

**👉 [Start Here: Complete Documentation](./docs/INDEX.md)**

### Quick Navigation

| Need | Link |
|------|------|
| 🚀 **Get started in 5 minutes** | [SETUP.md](./docs/guides/SETUP.md) |
| 🧪 **Run security tests** | [TESTING.md](./docs/guides/TESTING.md) |
| 🐳 **Deploy with Docker** | [config/docker/DEPLOYMENT.md](./config/docker/DEPLOYMENT.md) |
| 🏗️ **Understand the architecture** | [ARCHITECTURE.md](./docs/architecture/ARCHITECTURE.md) |
| 🔐 **Security policy & reporting** | [SECURITY.md](./docs/security/SECURITY.md) |
| 📦 **Dependencies & SBOM** | [SBOM.md](./docs/security/SBOM.md) |
| 🔐 **Cryptographic components** | [CBOM.md](./security/supply_chain/CBOM.md) |

---

📢 About the Author

This project is maintained by SperksWerks LLC — a Secure AI Engineering company specializing in:

- AI development and deployment
- LLM architecture security
- Threat modeling
- AI SDLC implementation
- Secure software consulting


