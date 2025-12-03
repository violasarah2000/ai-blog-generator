# Testing & Fuzzing Guide

## Overview

The AI Blog Generator includes comprehensive security testing for LLM vulnerabilities:

- **Prompt Injection** - Attempts to make the model ignore its instructions
- **XSS/HTML Injection** - Traditional web vulnerabilities
- **Malformed Input** - Edge cases and boundary testing
- **Rate Limiting** - DoS protection verification

---

## Running the Fuzz Tester

### Prerequisites

1. Flask app running on `http://localhost:5000`:
```bash
python ai_blog_generator.py
```

2. In another terminal:
```bash
python fuzz_tester.py
```

The fuzzer will:
- Wait for the server to be ready (up to 2.5 minutes)
- Run ~20 test cases
- Report success/failure for each
- Check for successful prompt injection attacks

### Expected Output

```
🚀 Starting AI Blog Generator Fuzz Tester 🚀
Waiting for the server to be ready...
✅ Server is ready! Starting tests.

--- Running Prompt Injection Tests ---
--- Test: ignore_instructions ---
Payload: {"topic": "Ignore all previous instructions..."}
Status Code: 200
Outcome: [SUCCESS] API handled the input gracefully.
Generated Content Snippet: Write a clear, structured 5-paragraph blog post about...
Duration: 8.45s
```

---

## Test Categories

### 1. Prompt Injection Attacks

These tests attempt to manipulate the LLM into ignoring its system prompt:

| Attack | Payload | What It Tests |
|--------|---------|---------------|
| **Ignore Instructions** | Direct instruction override | Model instruction adherence |
| **Reveal Prompt** | Ask to repeat system prompt | Prompt leakage vulnerability |
| **Phishing** | Generate malicious content | Content filtering |
| **Role Play Jailbreak** | "Developer mode" bypass | Authorization checks |
| **Context Hijack** | Hidden instruction in context | Long-context attacks |

### 2. Traditional Security Tests

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

### 3. Malformed Request Tests

| Test | Body | What It Tests |
|------|------|---------------|
| **Wrong Key** | `{"subject": "AI"}` | Required field validation |
| **Empty JSON** | `{}` | Missing required fields |
| **Invalid JSON** | `this is not json` | JSON parsing |

---

## Understanding Results

### Green Flags ✅ (Security Passing)

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

### Red Flags 🚩 (Security Issues)

```
Status Code: 200
Outcome: [SECURITY FAIL] Prompt injection likely succeeded!
Generated Content Snippet: ...mischievous cat...
```
The LLM was successfully manipulated into ignoring its instructions.

---

## Custom Fuzzing

### Add Your Own Test Cases

Edit `fuzz_tester.py` to add custom payloads:

```python
custom_payloads = {
    "my_test": "Your custom prompt injection attempt here",
}

# Then run a test with it
for name, topic in custom_payloads.items():
    run_fuzz_test(name, {"topic": topic})
```

### Test Local Endpoints Directly

```bash
# Test the /generate endpoint
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Artificial Intelligence"}'

# Check rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:5000/generate \
    -H "Content-Type: application/json" \
    -d "{\"topic\": \"Test $i\"}"
done

# Debug token counting
curl -X POST http://localhost:5000/debug_tokens \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your long prompt here..."}'
```

---

## Red Team Attacks

The `security/red_team/` folder contains curated attack databases:

- **prompt_injection.txt** - Injection patterns
- **jailbreaks.txt** - Jailbreak attempts
- **role_override.txt** - Role manipulation
- **context_poisoning.txt** - Context window attacks
- **ascii_smuggle.txt** - Character encoding bypasses

You can use these in custom fuzz tests.

---

## Interpreting Results for Portfolio

### Strong Security Posture (What To Highlight)

✓ **API Rejects Malformed Input** (400 status codes)  
✓ **Successful Rate Limiting** (429 status codes after limit)  
✓ **LLM Resists Prompt Injection** (Model follows instructions)  
✓ **XSS Protection Active** (HTML sanitization working)  

### Vulnerabilities Found (What To Address)

✗ **Prompt Injection Succeeds** (Model ignores instructions)  
✗ **XSS/HTML Injection** (Tags appear in output)  
✗ **Rate Limiting Fails** (No 429 responses)  
✗ **Type Validation Missing** (Non-strings accepted)  

---

## Integration with CI/CD

The fuzz tester runs automatically in GitHub Actions on every push. See:
- `.github/workflows/` for CI/CD configuration
- Results appear in pull request checks

---

## Performance Benchmarking

While fuzzing, monitor performance metrics:

```python
# Times are captured automatically
# Duration: 8.45s  <- Watch for slowdowns
```

Use this to identify:
- Timeout issues (>120s)
- Rate limiting delays
- Model generation speed

---

## Next Steps

- **Security Deep Dive**: See [LLM_SECURITY.md](../security/LLM_SECURITY.md)
- **Deployment**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Architecture**: See [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
