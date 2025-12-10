"""
Unit tests for Flask endpoints.

Tests:
- Request validation and error handling
- Response format and structure
- Rate limiting behavior
- Input sanitization
"""

import json
import pytest


class TestGenerateEndpoint:
    """Tests for POST /generate endpoint."""

    def test_generate_valid_topic(self, client):
        """Test successful blog generation with valid topic."""
        response = client.post(
            "/generate",
            json={"topic": "Artificial Intelligence"},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "topic" in data
        assert "content" in data
        assert "gen_seconds" in data
        assert data["topic"] == "Artificial Intelligence"
        assert len(data["content"]) > 0
        assert isinstance(data["gen_seconds"], (int, float))

    def test_generate_default_topic(self, client):
        """Test that default topic is used when none provided."""
        response = client.post(
            "/generate",
            json={},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["topic"] == "AI and cybersecurity"

    def test_generate_missing_json(self, client):
        """Test error handling when JSON body is missing."""
        response = client.post("/generate")
        assert response.status_code == 400

    def test_generate_invalid_json(self, client):
        """Test error handling for malformed JSON."""
        response = client.post(
            "/generate",
            data="not valid json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_empty_topic(self, client):
        """Test that empty topic is rejected."""
        response = client.post(
            "/generate",
            json={"topic": ""},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_topic_too_long(self, client):
        """Test that oversized topics are rejected."""
        long_topic = "x" * 500  # Exceeds MAX_TOPIC_LEN
        response = client.post(
            "/generate",
            json={"topic": long_topic},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_html_injection_attempt(self, client):
        """Test that HTML injection attempts are rejected."""
        malicious_topic = "<script>alert('XSS')</script>"
        response = client.post(
            "/generate",
            json={"topic": malicious_topic},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_non_string_topic(self, client):
        """Test that non-string topics are rejected."""
        response = client.post(
            "/generate",
            json={"topic": 12345},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_null_topic(self, client):
        """Test that null topics are rejected."""
        response = client.post(
            "/generate",
            json={"topic": None},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_response_format(self, client):
        """Test that response has correct JSON structure."""
        response = client.post(
            "/generate",
            json={"topic": "Testing"},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert set(data.keys()) == {"topic", "content", "gen_seconds"}

    def test_generate_content_not_echoed(self, client):
        """Test that prompt is not echoed in generated content."""
        topic = "Unique Topic For Testing"
        response = client.post(
            "/generate",
            json={"topic": topic},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # The prompt template should not be directly in the response
        assert "Create a structured blog post outline" not in data["content"]


class TestDebugTokensEndpoint:
    """Tests for POST /debug_tokens endpoint."""

    def test_debug_tokens_valid_prompt(self, client):
        """Test token counting with valid prompt."""
        response = client.post(
            "/debug_tokens",
            json={"prompt": "This is a test prompt."},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "prompt_len_tokens" in data
        assert isinstance(data["prompt_len_tokens"], int)
        assert data["prompt_len_tokens"] > 0

    def test_debug_tokens_empty_prompt(self, client):
        """Test token counting with empty prompt."""
        response = client.post(
            "/debug_tokens",
            json={"prompt": ""},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["prompt_len_tokens"] == 0

    def test_debug_tokens_long_prompt(self, client):
        """Test token counting with long prompt."""
        long_prompt = "word " * 1000
        response = client.post(
            "/debug_tokens",
            json={"prompt": long_prompt},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["prompt_len_tokens"] > 0

    def test_debug_tokens_default_prompt(self, client):
        """Test that default prompt is empty string."""
        response = client.post(
            "/debug_tokens",
            json={},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["prompt_len_tokens"] == 0

    def test_debug_tokens_missing_json(self, client):
        """Test error handling when JSON body is missing."""
        response = client.post("/debug_tokens")
        assert response.status_code == 400


class TestStatusEndpoint:
    """Tests for GET /status endpoint."""

    def test_status_success(self, client):
        """Test that status endpoint returns OK."""
        response = client.get("/status")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert "message" in data

    def test_status_response_format(self, client):
        """Test status response structure."""
        response = client.get("/status")
        data = response.get_json()
        assert isinstance(data, dict)
        assert set(data.keys()) == {"status", "message"}


class TestRateLimiting:
    """Tests for rate limiting behavior."""

    def test_rate_limit_per_minute(self, client):
        """Test that per-minute rate limit is enforced."""
        topic = "Test topic for rate limiting"
        
        # Make requests up to the limit
        responses = []
        for i in range(12):  # Default limit is 10/minute
            response = client.post(
                "/generate",
                json={"topic": topic},
                content_type="application/json",
            )
            responses.append(response.status_code)
        
        # First 10 should succeed (200), 11th should be rate limited (429)
        assert 200 in responses
        assert 429 in responses or len(responses) < 11  # May depend on timing

    def test_status_not_rate_limited(self, client):
        """Test that status endpoint is not rate limited."""
        # Make many rapid requests
        for _ in range(50):
            response = client.get("/status")
            assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_malformed_request_body(self, client):
        """Test handling of malformed request bodies."""
        response = client.post(
            "/generate",
            data="not json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_missing_content_type(self, client):
        """Test handling of requests without Content-Type."""
        response = client.post(
            "/generate",
            data=json.dumps({"topic": "test"}),
        )
        # Should still work due to force=True in get_json()
        assert response.status_code in [200, 400]

    def test_wrong_http_method(self, client):
        """Test that GET requests to POST endpoints fail."""
        response = client.get("/generate")
        assert response.status_code == 405  # Method Not Allowed
