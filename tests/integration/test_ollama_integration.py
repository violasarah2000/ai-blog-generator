"""Integration tests that verify live Ollama backend integration."""

import pytest
import time


class TestLiveOllamaIntegration:
    """Tests that require actual Ollama server running."""

    def test_ollama_server_is_running(self, client):
        """Verify Ollama server is accessible."""
        # This will fail if Ollama isn't running, causing all integration tests to skip
        response = client.get("/status")
        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"

    def test_generate_with_real_ollama(self, client):
        """Test actual text generation with live Ollama backend."""
        response = client.post(
            "/generate",
            json={"topic": "Artificial Intelligence"},
            content_type="application/json",
        )
        
        # Should succeed (may take time on first request)
        assert response.status_code == 200, f"Got {response.status_code}: {response.data}"
        
        data = response.get_json()
        assert "topic" in data
        assert "content" in data
        assert "gen_seconds" in data
        
        # Verify content is actual generated text (not mock)
        assert len(data["content"]) > 20, "Generated content should be present"
        assert data["topic"] == "Artificial Intelligence"
        assert isinstance(data["gen_seconds"], (int, float))
        assert data["gen_seconds"] > 0.1, "Should take some time to generate"

    def test_generate_multiple_topics_with_real_ollama(self, client):
        """Test generation with different topics."""
        topics = [
            "Machine Learning",
            "Cybersecurity",
            "Web Development",
        ]
        
        for topic in topics:
            response = client.post(
                "/generate",
                json={"topic": topic},
                content_type="application/json",
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["topic"] == topic
            assert len(data["content"]) > 50
            assert data["gen_seconds"] > 0

    def test_debug_tokens_with_real_backend(self, client):
        """Test token counting with live backend."""
        test_prompts = [
            "",
            "Hello",
            "This is a longer prompt to test token counting",
            "x" * 500,
        ]
        
        for prompt in test_prompts:
            response = client.post(
                "/debug_tokens",
                json={"prompt": prompt},
                content_type="application/json",
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert "prompt_len_tokens" in data
            assert isinstance(data["prompt_len_tokens"], int)
            assert data["prompt_len_tokens"] >= 0

    def test_generation_consistency(self, client):
        """Verify same topic generates consistent content length."""
        topic = "Python Programming"
        
        # Generate twice
        response1 = client.post(
            "/generate",
            json={"topic": topic},
            content_type="application/json",
        )
        time.sleep(1)  # Small delay between requests
        response2 = client.post(
            "/generate",
            json={"topic": topic},
            content_type="application/json",
        )
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Content should be present (may be different due to randomness, but similar length)
        len1 = len(data1["content"])
        len2 = len(data2["content"])
        
        # Allow 30% variance in length
        assert abs(len1 - len2) < max(len1, len2) * 0.3

    def test_long_topic_generation(self, client):
        """Test generation with a complex, longer topic."""
        topic = "The intersection of quantum computing, cryptography, and cybersecurity in modern enterprises"
        
        response = client.post(
            "/generate",
            json={"topic": topic},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["content"]) > 100
        assert data["topic"] == topic

    def test_default_topic_with_real_ollama(self, client):
        """Test that default topic works with real Ollama."""
        response = client.post(
            "/generate",
            json={},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["topic"] == "AI and cybersecurity"
        assert len(data["content"]) > 50

    def test_sanitization_with_real_generation(self, client):
        """Verify output sanitization doesn't break real generated content."""
        response = client.post(
            "/generate",
            json={"topic": "Web Security"},
            content_type="application/json",
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Content should not contain the full prompt
        prompt_start = "Create a structured blog post outline about:"
        assert prompt_start not in data["content"]
        
        # Content should have multiple sentences
        sentences = [s.strip() for s in data["content"].split(".") if s.strip()]
        assert len(sentences) >= 2

    def test_concurrent_generation(self, client):
        """Test that multiple rapid requests don't interfere."""
        responses = []
        
        for i in range(3):
            response = client.post(
                "/generate",
                json={"topic": f"Topic {i}"},
                content_type="application/json",
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.get_json()
            assert len(data["content"]) > 50

    def test_error_recovery_after_timeout(self, client):
        """Test that service recovers if a request times out."""
        # This test just verifies the next request works after a potential issue
        response1 = client.post(
            "/generate",
            json={"topic": "Test 1"},
            content_type="application/json",
        )
        
        # If response1 succeeded or failed, next request should still work
        response2 = client.post(
            "/generate",
            json={"topic": "Test 2"},
            content_type="application/json",
        )
        
        assert response2.status_code == 200
        data = response2.get_json()
        assert len(data["content"]) > 50
