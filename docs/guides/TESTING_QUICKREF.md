# Testing Quick Reference

## Running Tests - All Commands

```bash
# Run ALL tests with verbose output and coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_endpoints.py -v

# Run specific test class  
pytest tests/test_endpoints.py::TestGenerateEndpoint -v

# Run specific test
pytest tests/test_endpoints.py::TestGenerateEndpoint::test_generate_valid_topic -v

# Run with output (print statements visible)
pytest -s tests/test_endpoints.py

# Run tests with timing info
pytest tests/ -v --durations=10

# Run tests multiple times (catch flaky tests)
pytest tests/ --count=5

# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html
# Open: open htmlcov/index.html
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_endpoints.py        # Flask endpoint tests (HTTP behavior)
├── test_security.py         # Security & input validation tests
└── test_backends.py         # Model backend implementation tests
```

## Test Suites Explained

### 1. **Endpoint Tests** (`test_endpoints.py`)
Tests HTTP endpoints: `/generate`, `/debug_tokens`, `/status`

**What's Tested:**
- ✅ Valid requests return correct JSON structure
- ✅ Invalid/missing data returns 400 errors
- ✅ Rate limiting enforces limits
- ✅ HTTP methods are validated

**Run Just This:**
```bash
pytest tests/test_endpoints.py -v
```

**Key Tests:**
```
test_generate_valid_topic          → Valid blog generation works
test_generate_empty_topic          → Empty topics rejected  
test_generate_html_injection       → HTML injection blocked
test_rate_limit_per_minute         → Rate limits enforced
test_status_success                → Health check works
```

### 2. **Security Tests** (`test_security.py`)  
Tests input validation, type checking, and attack resistance

**What's Tested:**
- ✅ XSS/HTML injection attempts blocked
- ✅ SQL injection attempts handled safely
- ✅ Type validation (only strings accepted)
- ✅ Length limits enforced
- ✅ Prompt injection resistance
- ✅ Output sanitization working

**Run Just This:**
```bash
pytest tests/test_security.py -v
```

**Key Tests:**
```
test_rejects_html_tags             → <script> tags blocked
test_rejects_integer_topic         → Non-strings rejected
test_topic_length_limit            → Oversized input blocked
test_prompt_injection_attempt      → Injection attempts safe
test_output_not_echoed             → Prompt template hidden
```

### 3. **Backend Tests** (`test_backends.py`)
Tests model backend implementations and factory pattern

**What's Tested:**
- ✅ Backend factory creates correct implementation
- ✅ Ollama connection verification
- ✅ Token counting accuracy
- ✅ Error handling and fallbacks
- ✅ Configuration defaults

**Run Just This:**
```bash
pytest tests/test_backends.py -v
```

**Key Tests:**
```
test_create_ollama_backend         → Ollama backend created
test_ollama_verify_connection      → Connection check works
test_ollama_generate               → Text generation works
test_create_huggingface_backend    → HF backend created
```

## Common Test Scenarios

### Testing a Specific Feature
```bash
# Test just the /generate endpoint
pytest tests/test_endpoints.py::TestGenerateEndpoint -v

# Test just injection protection
pytest tests/test_security.py::TestPromptInjection -v

# Test just Ollama backend
pytest tests/test_backends.py::TestOllamaBackend -v
```

### Running One Test
```bash
# Copy the test name and run it
pytest tests/test_endpoints.py::TestGenerateEndpoint::test_generate_valid_topic -v
```

### Debugging a Failing Test
```bash
# Show print statements
pytest -s tests/test_endpoints.py::TestGenerateEndpoint::test_generate_valid_topic

# Drop into debugger on failure
pytest --pdb tests/test_endpoints.py::TestGenerateEndpoint::test_generate_valid_topic

# Show variable values in errors
pytest -vv tests/test_endpoints.py
```

### Check Test Coverage
```bash
# See which lines are tested
pytest tests/ --cov=app --cov-report=term-missing

# Generate HTML report (opens in browser)
pytest tests/ --cov=app --cov-report=html && open htmlcov/index.html
```

## Test Fixtures Available

All tests get access to these fixtures:

```python
def test_example(client, app):
    # client = Flask test client for making requests
    # app = Flask application configured for testing
    response = client.post("/generate", json={"topic": "AI"})
    assert response.status_code == 200
```

## Running Security Fuzz Tests

For comprehensive LLM security testing:

```bash
# Start app in one terminal
python run.py

# Run fuzz tests in another terminal
python fuzz_tester.py

# Results show security vulnerabilities
```

## CI/CD Integration

Tests automatically run on:
- **Every push** to GitHub
- **Pull requests** 
- **Schedule**: Daily at midnight

Check results in: GitHub Actions → Pull Requests

## Test Statistics

**Total Tests**: ~60+
- **Endpoint tests**: ~15
- **Security tests**: ~30
- **Backend tests**: ~15+

**Expected Results**: All passing ✅

## Portfolio Highlights

When presenting this to interviewers, emphasize:

✅ **Comprehensive Test Coverage**  
- Unit tests for individual components
- Integration tests for API behavior
- Security tests for attack resistance

✅ **Professional Test Practices**
- Organized test structure
- Clear fixture management
- Proper mocking of dependencies

✅ **Security Testing Sophistication**
- LLM attack detection (prompt injection)
- Input validation and sanitization
- Type checking and boundary testing

## Next Steps

1. **Run All Tests**: `pytest tests/ -v`
2. **Check Coverage**: `pytest tests/ --cov=app --cov-report=html`
3. **Run Fuzz Tests**: `python fuzz_tester.py`
4. **Add New Tests**: Copy pattern from existing tests

For detailed testing guide, see: [TESTING_COMPREHENSIVE.md](./TESTING_COMPREHENSIVE.md)
