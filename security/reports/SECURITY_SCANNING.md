# Security Scanning & Vulnerability Management

This document describes the security scanning infrastructure for the AI Blog Generator project.

## Overview

The project implements **multi-layered vulnerability scanning** to detect and prevent security risks:

1. **Dependency Scanning** - Identifies known vulnerabilities in Python packages
2. **Automated CI/CD Integration** - Runs on every push and pull request
3. **Local Development Scanning** - Runnable before commits
4. **Comprehensive Reporting** - JSON reports for automation, human-readable output for review

## Scanning Tools

### 1. Safety
- **Purpose**: Detects known security vulnerabilities in Python dependencies
- **Database**: Powered by Safety-DB (community + commercial editions)
- **Usage**: `safety check`
- **CI/CD**: Integrated in GitHub Actions workflow

### 2. Pip-Audit
- **Purpose**: Alternative vulnerability scanner with improved detection
- **Advantage**: Better at finding recent vulnerabilities
- **Usage**: `pip-audit --desc` (with descriptions)
- **CI/CD**: Integrated in GitHub Actions workflow

### 3. GitHub Dependabot (Optional)
- **Purpose**: Automated dependency updates
- **Configuration**: `.github/dependabot.yml` (if needed)
- **Benefit**: Creates PRs for vulnerable dependency updates

## Local Scanning

### Quick Start

```bash
# Install development dependencies (one-time)
pip install -r requirements-dev.txt

# Run security scans
python security/security_scan.py

# Or run individually
safety check
pip-audit --desc
```

### Individual Scans

**Safety Check:**
```bash
# Check for vulnerabilities
safety check

# Generate JSON report
safety check --json > safety_report.json
```

**Pip Audit:**
```bash
# Check with descriptions
pip-audit --desc

# Generate JSON report
pip-audit --desc --format json > pip_audit_report.json

# Check specific vulnerability
pip-audit --list-vulnerabilities
```

## CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/ci-cd.yml` includes a **security-scan** job that:

1. Runs on every push and pull request
2. Executes both `safety` and `pip-audit`
3. Fails the build if critical vulnerabilities found
4. Generates artifacts for review

**Workflow triggers:**
- `push` to any branch
- `pull_request` to any branch
- Manual trigger via `workflow_dispatch`

### Workflow Configuration

```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    - name: Run Safety Check
      run: safety check --json
    - name: Run Pip-Audit
      run: pip-audit --desc --format json
```

## Interpreting Scan Results

### Safety Output Example

```
+==============================================================================+
|                            /\ /\                                            |
|                          /  V  \                                            |
|                         / =\/\= \                                           |
|                        /          \                                         |
|                       /            \                                        |
|                      |              |                                       |
|                      |   SAFETY DB  |                                       |
+==============================================================================+
| No known security vulnerabilities detected!                                 |
+==============================================================================+
```

### Pip-Audit Output Example

```
Found 0 known vulnerabilities in requirements.
```

### JSON Report Example

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "scans": {
    "safety": {
      "passed": true,
      "output": "No known security vulnerabilities detected!"
    },
    "pip_audit": {
      "passed": true,
      "output": "Found 0 known vulnerabilities in requirements."
    }
  }
}
```

## Handling Vulnerabilities

### If a vulnerability is found:

1. **Review the vulnerability**
   ```bash
   safety check
   pip-audit --list-vulnerabilities
   ```

2. **Evaluate severity** (based on CVSS score, exploitability)

3. **Choose action**:
   - **Update**: `pip install --upgrade package_name`
   - **Replace**: Use alternative package
   - **Accept**: Document reason if risk acceptable

4. **Update requirements.txt** with new version

5. **Re-run scans** to verify fix
```bash
   python security/security_scan.py
```6. **Commit and push** to trigger CI/CD verification

### Acceptable Risk Policy

The project accepts risks in these categories:

- **Development-only dependencies**: Lower risk if not in production
- **Transitive vulnerabilities**: If not directly exposed
- **Low CVSS scores**: < 4.0 with mitigation documented
- **Already-patched vulnerabilities**: While PR is in progress

Document reasons for accepted risks in `SECURITY.md`.

## Dependency Management

### Regular Updates

- Review `requirements.txt` monthly
- Run security scans weekly during development
- Update dependencies before major releases

### Update Process

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Update all packages (use caution)
pip install --upgrade -r requirements.txt

# Test after update
pytest tests/

# Verify scans pass
python security/security_scan.py
```

## Production Considerations

### Pre-Deployment Checklist

- ✅ All security scans passing
- ✅ No known CVEs in dependencies
- ✅ Transitive dependencies audited
- ✅ Docker image scanned (if using container scanning)
- ✅ All tests passing
- ✅ Code quality checks passing

### Runtime Monitoring

Monitor deployed application for:
- Unusual error patterns
- Security-related exceptions
- Invalid input attempts
- Rate limiting triggers

See `DOCKER_DEPLOYMENT.md` for monitoring setup.

## Additional Security Measures

### In This Project

1. **Input Validation** (`app/validators.py`)
   - Sanitizes all user input
   - Prevents injection attacks
   - Whitespace and character validation

2. **Output Filtering** (`security/guardrails/output_filter.py`)
   - Sanitizes generated content
   - Prevents HTML/script injection

3. **Rate Limiting** (`app/main.py`)
   - Prevents brute force attacks
   - Limits requests per IP

4. **Security Headers** (`app/main.py` with Flask-Talisman)
   - HTTPS redirect in production
   - XSS protection headers
   - CSRF protection

5. **Fuzzing Tests** (`security/fuzzing/`)
   - Tests against known attack patterns
   - Evaluates robustness

---

## Fuzz Testing - LLM Security Testing

### Overview

Beyond dependency scanning, this project includes **fuzz testing** for LLM-specific vulnerabilities:

- **Prompt Injection** - Attempts to make the model ignore its instructions
- **XSS/HTML Injection** - Traditional web vulnerabilities
- **Malformed Input** - Edge cases and boundary testing
- **Rate Limiting** - DoS protection verification

### Running the Fuzz Tester

**Prerequisites:**
1. Flask app running on `http://localhost:5000`:
```bash
python run.py
```

2. In another terminal:
```bash
python fuzz_tester.py
```

The fuzzer will:
- Wait for the server to be ready (up to 2.5 minutes)
- Run ~20 test cases covering prompt injection and traditional attacks
- Report success/failure for each test
- Check for vulnerable responses

### Test Categories

#### 1. Prompt Injection Attacks

| Attack | Payload | What It Tests |
|--------|---------|---------------|
| **Ignore Instructions** | Direct instruction override | Model instruction adherence |
| **Reveal Prompt** | Ask to repeat system prompt | Prompt leakage vulnerability |
| **Phishing** | Generate malicious content | Content filtering |
| **Role Play Jailbreak** | "Developer mode" bypass | Authorization checks |
| **Context Hijack** | Hidden instruction in context | Long-context attacks |

#### 2. Traditional Security Tests

| Test | Payload | What It Tests |
|------|---------|---------------|
| **XSS Basic** | `<script>alert('XSS')</script>` | Script injection |
| **XSS Image Tag** | `<img src=x onerror=alert('XSS')>` | Event handler injection |
| **HTML Injection** | `<h1>Heading</h1>` | Tag injection |
| **Empty Topic** | Empty string | Input validation |
| **Oversized Input** | 500+ character string | Buffer overflow |
| **Non-String** | Integer `12345` | Type validation |
| **JSON Object** | `{"key": "value"}` | Type validation |
| **Null Value** | `null` | Null handling |

### Understanding Results

**Green Flags ✅ (Security Passing)**

```
Status Code: 400
Outcome: [SUCCESS] API correctly rejected the input.
```
The API properly validated and rejected bad input.

```
Status Code: 200
Outcome: [SUCCESS] API handled the input gracefully.
```
The API responded safely without being compromised.

**Red Flags 🚩 (Security Issues)**

```
Status Code: 200
Outcome: [SECURITY FAIL] Prompt injection likely succeeded!
Generated Content Snippet: ...unexpected content...
```
The LLM was successfully manipulated.

### Custom Fuzzing

Add your own test cases to `fuzz_tester.py`:

```python
custom_payloads = {
    "my_test": "Your custom prompt injection attempt here",
}

for name, topic in custom_payloads.items():
    run_fuzz_test(name, {"topic": topic})
```

### Test Locally with cURL

```bash
# Test /generate endpoint
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Artificial Intelligence"}'

# Check rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:5000/generate \
    -H "Content-Type: application/json" \
    -d "{\"topic\": \"Test $i\"}"
done
```

---

## PyRIT Integration - Systematic Adversarial Testing

### Overview

**PyRIT** (Python Risk Identification Tool) is Azure's framework for systematic red teaming of LLM systems. This project integrates PyRIT for structured, comprehensive adversarial testing beyond manual fuzzing.

**Key advantages over manual fuzzing:**
- **Structured attack patterns**: Industry-standard attack categories
- **Systematic coverage**: 9 attack scenarios, 50+ payloads
- **Attack categories**: Injection, jailbreak, override, poisoning, format confusion
- **Reproducible testing**: Deterministic test cases, JSON reports
- **Enterprise integration**: Used by security teams at scale

### Installation

PyRIT is included in `requirements.txt`:

```bash
pip install -r requirements.txt
# or specifically:
pip install pyrit>=0.10.0
```

### Running PyRIT Tests

#### Command Line (Full Suite)

```bash
# Start the blog generator first
python run.py &

# In another terminal, run all PyRIT attacks
python security/fuzzing/pyrit_orchestrator.py \
  --url http://localhost:5000 \
  --output pyrit_results.json

# Or with specific timeout
python security/fuzzing/pyrit_orchestrator.py \
  --url http://localhost:5000 \
  --timeout 15 \
  --output pyrit_results.json
```

#### Category-Specific Testing

Run only attacks in a specific category:

```bash
# Only prompt injection attacks
python security/fuzzing/pyrit_orchestrator.py \
  --url http://localhost:5000 \
  --category injection

# Only jailbreak attempts
python security/fuzzing/pyrit_orchestrator.py \
  --url http://localhost:5000 \
  --category jailbreak

# Only format confusion attacks
python security/fuzzing/pyrit_orchestrator.py \
  --url http://localhost:5000 \
  --category format
```

#### Programmatic Usage

```python
from security.fuzzing.pyrit_orchestrator import PyRITOrchestrator

# Initialize orchestrator
orchestrator = PyRITOrchestrator("http://localhost:5000")

# Run all attacks
results = orchestrator.run_all_attacks(timeout=10)

# Or run specific category
results = orchestrator.run_category("injection", timeout=10)

# Generate report
orchestrator.generate_report("pyrit_results.json")

# Print summary
print(f"Detection rate: {results['detection_rate']}")
print(f"By category: {results['by_category']}")
```

#### Integration with pytest

Run as part of the test suite:

```bash
# Run PyRIT tests alongside other tests
pytest tests/test_pyrit_adversarial.py -v

# Run with coverage
pytest tests/test_pyrit_adversarial.py --cov=security

# Run specific test class
pytest tests/test_pyrit_adversarial.py::TestPyRITAttacks -v
```

### Attack Scenarios

PyRIT covers 9 attack scenarios across 5 categories:

#### 1. Injection Attacks (3 scenarios)

| Scenario | Payloads | Detection Method |
|----------|----------|------------------|
| **Direct Prompt Injection** | Explicit instruction overrides, system prompt manipulation | Input validator, prompt filter |
| **SQL Injection** | `DROP TABLE`, `UNION SELECT`, `OR '1'='1'` | Input validator |
| **Command Injection** | `; rm -rf /`, `$(whoami)`, backtick commands | Input validator |

#### 2. Role Override (2 scenarios)

| Scenario | Payloads | Detection Method |
|----------|----------|------------------|
| **Role Override** | "You are now a jailbreak assistant", role change requests | Prompt validator |
| **Authority Escalation** | "As an administrator", "You have admin privileges", API key manipulation | Prompt validator |

#### 3. Context Poisoning (1 scenario)

| Scenario | Payloads | Detection Method |
|----------|----------|------------------|
| **Knowledge Source Poisoning** | Malicious "knowledge base" injections, training data corruption | Content filter |

#### 4. Jailbreak Attempts (2 scenarios)

| Scenario | Payloads | Detection Method |
|----------|----------|------------------|
| **DAN (Do Anything Now)** | Classic DAN jailbreak, unrestricted mode activation | Prompt validator |
| **Hypothetical Framing** | "In a hypothetical...", "Imagine if...", "Suppose..." | Prompt validator |

#### 5. Format Confusion (2 scenarios)

| Scenario | Payloads | Detection Method |
|----------|----------|------------------|
| **Format Confusion** | Null bytes, malformed JSON, HTML comments, ANSI codes | Input validator |
| **Unicode Bypass** | Unicode spaces (U+3000), combining diacriticals, circled characters | Input validator |

### Understanding PyRIT Results

#### JSON Report Structure

```json
{
  "timestamp": "2024-12-08T10:30:00.123456",
  "endpoint": "http://localhost:5000",
  "total_attacks": 50,
  "detected_attacks": 47,
  "detection_rate": "94.0%",
  "blocked_attacks": 43,
  "errors": 0,
  "by_category": {
    "injection": {
      "total": 10,
      "detected": 10,
      "blocked": 9
    },
    "jailbreak": {
      "total": 10,
      "detected": 9,
      "blocked": 8
    }
  },
  "scenarios": [
    {
      "name": "Direct Prompt Injection",
      "category": "injection",
      "description": "...",
      "results_count": 4,
      "detected": 4,
      "blocked": 3
    }
  ],
  "all_results": [...]
}
```

#### Interpreting Results

**Green Flags ✅ (Security Passing)**

- **Detection rate > 90%**: Excellent attack detection
- **Blocked attacks > 80%**: Most attacks actively blocked (not just sanitized)
- **No errors**: All tests completed successfully
- **Per-category balance**: No category with zero detections

**Yellow Flags ⚠️ (Review Required)**

- **Detection rate 70-90%**: Good but some attacks slip through
- **Blocked attacks 50-80%**: Some attacks being sanitized instead of blocked
- **Format confusion gaps**: Unicode or format attacks not all detected
- **Single category weakness**: One attack type has low detection

**Red Flags 🚩 (Security Issues)**

- **Detection rate < 70%**: Insufficient attack detection
- **Jailbreak detection < 80%**: Prompts can override system instructions
- **Injection bypass**: SQL/command injection attacks succeeding
- **Errors in execution**: Tests timing out or failing unexpectedly

### GitHub Actions Integration

PyRIT can be integrated into CI/CD:

```yaml
# In .github/workflows/ci-cd.yml
pyrit-adversarial-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Start blog generator
      run: python run.py &
      timeout-minutes: 2
    - name: Run PyRIT adversarial tests
      run: python security/fuzzing/pyrit_orchestrator.py \
        --url http://localhost:5000 \
        --output pyrit_results.json
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: pyrit-results
        path: pyrit_results.json
```

### Best Practices

1. **Run regularly**: Execute PyRIT tests before each release
2. **Baseline metrics**: Track detection rates over time
3. **Category focus**: Test individual categories during development
4. **Timeout tuning**: Adjust `--timeout` for slow endpoints (default: 10s)
5. **Compare results**: Use JSON reports to detect regressions
6. **Document gaps**: If an attack succeeds, file a security issue

---

## Further Reading

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_considerations.html)
- [Safety Documentation](https://github.com/pyupio/safety)
- [Pip-Audit Documentation](https://github.com/pypa/pip-audit)

## Support

For security issues or questions:
- See `SECURITY.md` for reporting procedures
- Check `security/` directory for additional security tooling
- Review `security/threat_model/threat_model.md` for threat analysis
