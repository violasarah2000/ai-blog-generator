# Cryptographic Bill of Materials (CBOM)

**Project**: AI Blog Generator  
**Generated**: December 2, 2025  
**Version**: 1.0  
**Status**: Production-Ready

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Active Components | 2 | Production |
| Proposed Components | 3 | Future |
| Total | 5 | - |

---

## Active Cryptographic Components

### 1. TLS/HTTPS
- **Algorithm**: TLS 1.2/1.3
- **Library**: Flask-Talisman v1.1.0
- **Location**: `app/main.py:39`
- **Key Size**: Variable (RSA/ECDSA per server config)
- **Purpose**: Transport layer security, HTTPS enforcement
- **Status**: ✅ Active (production only)
- **Risk Level**: ✅ LOW (industry standard, delegated to web server)
- **Configuration**: Enabled only when `FLASK_ENV == "production"`

**Implementation Details:**
```python
Talisman(app, content_security_policy=None)
```
- Enforces HTTPS redirect
- Sets security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Prevents clickjacking attacks
- Delegates encryption to Gunicorn/reverse proxy

### 2. Rate Limiting (HMAC)
- **Algorithm**: HMAC-SHA1
- **Library**: Flask-Limiter v2.9.2 (internal mechanism)
- **Location**: `app/main.py:44-47`
- **Purpose**: Rate limit token generation
- **Status**: ✅ Active (internal use only)
- **Risk Level**: ✅ LOW (not protecting user data)
- **Configuration**: 10 requests/minute per IP, 100 requests/hour

**Implementation Details:**
```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        "100/hour",
        "10/minute",
    ],
)
```
- Uses client IP for rate limit tracking
- HMAC internally for token generation
- Not cryptographically protecting user input

---

## Proposed Cryptographic Components

### 3. API Authentication (JWT)
- **Algorithm**: HS256 (HMAC-SHA256) or RS256 (RSA-SHA256)
- **Library**: PyJWT v2.x (not currently installed)
- **Proposed Location**: `app/auth.py`
- **Key Size**: 256-bit (HS256) or 2048-bit+ (RS256)
- **Purpose**: Optional API key authentication for client authorization
- **Status**: 📋 Proposed (not yet implemented)
- **Timeline**: Q1 2026 (if deploying to public internet)
- **Priority**: LOW
- **Notes**: 
  - Only add if accepting requests from untrusted sources
  - Current deployment is local/Docker, so not needed yet
  - Use RS256 in production (asymmetric) rather than HS256 (symmetric)

**When to Implement:**
- Deploying to public cloud
- Multiple external clients need access
- Need audit trail of "who called what"

### 4. Data Encryption (AES-GCM)
- **Algorithm**: AES-256-GCM
- **Library**: cryptography v41.x (not currently installed)
- **Proposed Location**: `security/encryption.py`
- **Key Size**: 256-bit
- **Mode**: Galois/Counter Mode (authenticated encryption)
- **Purpose**: Optional encryption at rest (if database added)
- **Status**: 📋 Proposed (not yet implemented)
- **Timeline**: Q2 2026 (if persisting sensitive data)
- **Priority**: LOW
- **Notes**:
  - Current app is stateless (no database)
  - Use GCM mode for authenticated encryption
  - Integrate with key management service (AWS KMS, Vault, etc.)
  - Never implement key generation yourself

**When to Implement:**
- Adding database to persist data
- Storing user-generated content
- Compliance requirement (GDPR, HIPAA, etc.)

### 5. Code Signing (GPG)
- **Algorithm**: RSA-4096 + SHA-256
- **Tool**: GPG (GNU Privacy Guard)
- **Location**: Git commits (`.git/` configuration)
- **Purpose**: Commit authentication and non-repudiation
- **Status**: 📋 Proposed (manual process, see SECURITY_SCANNING.md)
- **Timeline**: Before first push to production
- **Priority**: MEDIUM
- **Notes**:
  - Ensures commits are authenticated
  - Provides non-repudiation (can't deny sending a commit)
  - Requires GPG key generation (one-time setup)
  - Can enforce signed commits in GitHub branch protection

**Implementation:**
```bash
gpg --full-generate-key
git config --global commit.gpgsign true
```

---

## Current Security Posture

| Aspect | Status | Notes |
|--------|--------|-------|
| Transport Security | ✅ Good | TLS 1.2/1.3 enforced in production |
| At-Rest Encryption | ⚠️ N/A | No persistent data storage |
| Authentication | ⚠️ None | Stateless API, rate-limited by IP |
| Input Validation | ✅ Excellent | Bleach HTML sanitization in place |
| Output Sanitization | ✅ Excellent | Removes prompts and URLs |
| Crypto Agility | ✅ Good | Can upgrade TLS/algorithms easily |
| Key Management | ✅ Good | No key handling in application code |
| Dependency Scanning | ✅ Active | safety + pip-audit in CI/CD |

---

## Cryptographic Dependencies

### Currently Installed (In requirements.txt)
```
flask-talisman==1.1.0      # TLS/HTTPS security headers
flask-limiter==2.9.2       # Rate limiting (uses HMAC internally)
```

### Future Optional Dependencies
```
PyJWT>=2.0                  # JWT token signing/verification
cryptography>=41.0          # AES encryption and key management
```

### Python Standard Library (Always Available)
```
hashlib                     # SHA-256, HMAC
secrets                     # Secure random number generation
ssl                         # TLS configuration
```

---

## Vulnerability Status

### Current Vulnerabilities (as of Dec 2, 2025)
- torch 2.2.2: 6 known CVEs (mitigated via input validation + trusted model sources)
- pip 25.1: 1 CVE (file overwrite - system level, not app critical)
- werkzeug 3.1.3: 1 CVE (Windows device names - not applicable in Docker Linux)

**Mitigations in Place:**
✅ Input validation prevents untrusted data execution  
✅ Model loading restricted to trusted sources (local Ollama, authenticated HuggingFace)  
✅ Docker deployment uses Linux (not vulnerable to werkzeug Windows CVE)  
✅ Transformers upgraded to 4.53.0 (fixes all critical RCE/ReDoS vulnerabilities)

See `VULNERABILITY_ASSESSMENT.md` for detailed analysis.

---

## Compliance & Standards

This CBOM follows:
- **CBOM v1.0** community standard (cryptographic equivalent of SBOM)
- **NIST SP 800-175B**: Recommendation for Cryptographic Key Management
- **CycloneDX**: Compatible with Software Bill of Materials ecosystem
- **OWASP**: Secure coding practices

---

## Implementation Roadmap

| Phase | Component | Effort | When | Depends On |
|-------|-----------|--------|------|-----------|
| ✅ Phase 0 | CBOM Documentation | 30 min | Dec 2025 | - |
| 📋 Phase 1 | GPG Code Signing | 1 hour | Before push | - |
| 📋 Phase 2 | JWT API Auth | 2 hours | Q1 2026 | Public deployment |
| 📋 Phase 3 | AES Encryption | 3 hours | Q2 2026 | Database addition |
| 📋 Phase 4 | Hardware Security Key | TBD | Future | Enterprise requirement |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│           Client Request                             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  TLS 1.2/1.3         │ ◄── Active: Flask-Talisman
        │  (Transport Layer)    │
        └──────────────┬───────┘
                       │
                       ▼
        ┌──────────────────────┐
        │  Rate Limiting       │ ◄── Active: Flask-Limiter
        │  (IP-based HMAC)     │
        └──────────────┬───────┘
                       │
                       ▼
        ┌──────────────────────┐
        │  Input Validation    │ ◄── Implemented: Bleach
        │  (HTML sanitization) │
        └──────────────┬───────┘
                       │
                       ▼
        ┌──────────────────────┐
        │  LLM Processing      │
        │  (Ollama/HuggingFace)│
        └──────────────┬───────┘
                       │
                       ▼
        ┌──────────────────────┐
        │  Output Filtering    │ ◄── Implemented: Bleach
        │  (URL removal)       │
        └──────────────┬───────┘
                       │
                       ▼
        ┌──────────────────────┐
        │  TLS Encryption      │ ◄── Response back to client
        │  (Return to client)  │
        └──────────────────────┘
```

---

## Security Review Checklist

- [x] TLS/HTTPS configured for production
- [x] Rate limiting implemented
- [x] Input validation in place
- [x] Output sanitization in place
- [x] No sensitive data stored
- [x] Dependency scanning active
- [x] Vulnerability assessment complete
- [ ] Code signing enabled (Phase 1)
- [ ] API authentication implemented (Phase 2, if needed)
- [ ] Database encryption implemented (Phase 3, if needed)

---

## Review & Approval

| Date | Reviewer | Status | Notes |
|------|----------|--------|-------|
| 2025-12-02 | Sarah Perkins | ✅ Approved | Initial CBOM creation |
| - | Security Team | Pending | Enterprise review |
| - | Compliance | Pending | Regulatory assessment |

---

## Key Management Policy

**Current Status**: No key management needed (no application-level encryption)

**Future Policy** (when implementing encryption):
- ✅ Use cloud provider KMS (AWS KMS, Azure Key Vault, GCP Cloud KMS)
- ✅ Never store keys in code or `.env` files
- ✅ Rotate keys annually minimum
- ✅ Use separate keys per environment
- ✅ Implement audit logging for key access

---

## Contact & Questions

For questions about this CBOM:
- **Security Policy**: See `SECURITY.md`
- **Threat Model**: See `security/threat_model/threat_model.md`
- **Vulnerabilities**: See `VULNERABILITY_ASSESSMENT.md`
- **Scanning**: See `SECURITY_SCANNING.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-02 | Initial CBOM creation with current + proposed components |

---

**Last Updated**: December 2, 2025  
**Next Review**: Q1 2026 or after major architectural changes
