# Security Policy

**AI Blog Generator** – Secure AI Engineering Demonstration  
SperksWerks LLC

---

## 🔐 Overview

This repository is intentionally designed as a **demonstration project** for modern AI security testing and secure SDLC practices. It includes examples of:

- ✓ Secure SDLC workflows
- ✓ Traditional SAST/DAST integration
- ✓ LLM-specific security testing
- ✓ Automated adversarial fuzzing
- ✓ Threat modeling for AI architectures
- ✓ Secure coding best practices
- ✓ Code scanning and dependency management

The goal is to showcase professional capabilities in **AI Security Engineering**, including emerging practices required for safe AI application development.

---

## 🛡️ Supported Security Testing

### 1. Static Application Security Testing (SAST)

This project integrates:

- **GitHub CodeQL** - Semantic code analysis
- **Python Bandit** - Security linting
- **Dependency Scanning** (Dependabot/Mend) - Vulnerability tracking
- **Semgrep** (optional) - Custom security rules

All findings are automatically surfaced in pull requests and the GitHub Security tab.

**Runs**: Every push and pull request

### 2. Dynamic Application Security Testing (DAST)

When deployed locally or in staging, the following can be run:

- **OWASP ZAP API scan** - Automated API fuzzing
- **Flask security headers validation** - HTTP security headers
- **Local runtime behavior checks** - Integration tests

**Manual**: Can be triggered post-deployment

### 3. AI / LLM Security Testing

This repository includes comprehensive LLM-specific testing:

#### LLM Fuzzing Framework
- Automated adversarial input generation
- Prompt injection testing
- Output safety and hallucination detection
- Response boundary testing (long context, malformed input, nested inputs)

#### AI Red Team Exercises
- Model inversion attempts
- Prompt-based evasion tactics
- Guardrail bypass attempts
- Evaluation of model drift and unexpected reasoning

#### Supply Chain Security for LLMs
- Model hash verification
- Model provenance tracking (Ollama / HuggingFace)
- Container signing and rebuild transparency
- SBOM generation and tracking

**Runs**: Weekly + on-demand via `python security/supply_chain/generate_sbom.py`

---

## 🔰 Threat Model

The architecture is analyzed using:

- **STRIDE** - Threat categorization (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- **PASTA** (AI-adapted) - Process for Attack Simulation and Threat Analysis
- **MITRE ATLAS** - LLM-specific threat matrix

See [THREAT_MODEL.md](./THREAT_MODEL.md) for complete analysis.

---

## ❗ Reporting a Vulnerability

If you discover a vulnerability or unexpected model behavior:

### Security Advisories

**Preferred Method**: Submit via GitHub Security Advisory
1. Navigate to: **Security → Advisories → New draft advisory**
2. Provide clear reproduction steps
3. Include affected version(s) and components

### Email Reporting

For sensitive issues, email: **studio@sperkswerks.ai**

### Responsible Disclosure Guidelines

To keep security disclosures responsible:

1. **Provide clear reproduction path** - Step-by-step instructions
2. **Don't disclose publicly** - Until discussed and remediated
3. **Include context** - Model version, backend used, exact inputs
4. **Suggest fixes** - If possible, propose mitigation strategies

### Expected Timeline

- **Initial Response**: Within 2 business days
- **Investigation**: Within 1 week
- **Fix + Release**: Estimated timeline provided
- **Public Disclosure**: After patch is released

---

## 🔐 Security Best Practices Implemented

### Input Validation
- ✓ Max topic length enforced (200 chars)
- ✓ HTML/XSS sanitization via Bleach
- ✓ JSON validation and error handling
- ✓ Type checking for all inputs

### Rate Limiting
- ✓ 10 requests/minute per IP
- ✓ 100 requests/hour per IP
- ✓ Configurable via `.env` file

### Output Filtering
- ✓ Prompt echoing removed
- ✓ URL injection prevention
- ✓ Malicious output detection framework
- ✓ Configurable guardrails

### Model Safety
- ✓ Token limits enforced
- ✓ Timeout protection (120 seconds)
- ✓ Retry logic for failed generations
- ✓ Temperature controls

### Dependency Management
- ✓ All versions pinned in `requirements.txt`
- ✓ Weekly vulnerability scans (pip-audit)
- ✓ SBOM generation in CycloneDX format
- ✓ Supply chain security tracking

### Network Security
- ✓ HTTPS support (Flask-Talisman)
- ✓ Security headers configured
- ✓ CORS restrictions possible
- ✓ API key framework ready

---

## 🚫 Responsible AI Use

This project is **not intended** for:
- ✗ Generating harmful, illegal, or malicious content
- ✗ Circumventing model safety mechanisms
- ✗ Unauthorized access to systems
- ✗ Creating deepfakes or misinformation

This project **is designed** for:
- ✓ Security research and testing
- ✓ Educational purposes
- ✓ Building safer AI systems
- ✓ Demonstrating security best practices

---

## 📋 CI/CD Security Pipeline

### Automated Checks

On every pull request, the following run:

1. **CodeQL Analysis** - Semantic code scanning
2. **Dependency Audit** - pip-audit for vulnerabilities
3. **SBOM Generation** - CycloneDX format
4. **Security Tests** - Fuzz testing and guardrail validation
5. **Linting & Type Checking** - Code quality

### Manual Approvals

Before merging to `main`:

- [ ] All security checks pass
- [ ] No new vulnerabilities introduced
- [ ] Documentation updated
- [ ] Code review completed

---

## 🙏 Acknowledgements

This project is part of the **Secure AI Studio** program at SperksWerks LLC, dedicated to elevating the security posture of AI-driven software.

**Maintainer**: Sarah Perkins ([@violasarah2000](https://github.com/violasarah2000))  
**Organization**: SperksWerks LLC  
**Contact**: studio@sperkswerks.ai

---

## 📚 Additional Resources

- [OWASP LLM Security Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS Framework](https://atlas.mitre.org/)
- [NIST AI Risk Management Framework](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- [CycloneDX Standard](https://cyclonedx.org/)
