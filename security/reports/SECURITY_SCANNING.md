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
python scripts/security_scan.py

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
   python scripts/security_scan.py
   ```

6. **Commit and push** to trigger CI/CD verification

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
python scripts/security_scan.py
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
