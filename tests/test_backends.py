"""
Unit tests for model backends.

Tests:
- Backend initialization and configuration
- Token counting
- Error handling
- Backend selection logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.model_backend import create_backend, OllamaBackend, ModelBackend


class TestBackendFactory:
    """Tests for the backend factory function."""

    def test_create_ollama_backend(self):
        """Test creating Ollama backend."""
        with patch.object(OllamaBackend, "_verify_connection"):
            backend = create_backend(
                "ollama",
                ollama_base_url="http://localhost:11434",
                ollama_model="stablelm-zephyr:3b",
            )
            assert isinstance(backend, OllamaBackend)
            assert backend.model_name == "stablelm-zephyr:3b"

    def test_create_ollama_backend_defaults(self):
        """Test Ollama backend uses correct defaults."""
        with patch.object(OllamaBackend, "_verify_connection"):
            backend = create_backend("ollama")
            assert backend.base_url == "http://localhost:11434"
            assert backend.model_name == "stablelm-zephyr:3b"

    def test_factory_case_insensitive(self):
        """Test that backend type is case-insensitive."""
        with patch.object(OllamaBackend, "_verify_connection"):
            backend1 = create_backend("OLLAMA")
            backend2 = create_backend("Ollama")
            backend3 = create_backend("ollama")
            
            assert isinstance(backend1, OllamaBackend)
            assert isinstance(backend2, OllamaBackend)
            assert isinstance(backend3, OllamaBackend)

    def test_invalid_backend_type(self):
        """Test that invalid backend type raises error."""
        with pytest.raises(ValueError):
            create_backend("invalid_backend")


class TestOllamaBackend:
    """Tests for OllamaBackend implementation."""

    @patch("app.model_backend.requests.get")
    def test_ollama_verify_connection_success(self, mock_get):
        """Test successful connection to Ollama."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [{"name": "stablelm-zephyr:3b"}]
        }
        mock_get.return_value = mock_response
        
        backend = OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")
        assert backend.base_url == "http://localhost:11434"

    @patch("app.model_backend.requests.get")
    def test_ollama_verify_connection_failure(self, mock_get):
        """Test connection failure raises error."""
        mock_get.side_effect = Exception("Connection refused")
        
        with pytest.raises(RuntimeError):
            OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")

    @patch("app.model_backend.requests.get")
    @patch("app.model_backend.requests.post")
    def test_ollama_generate(self, mock_post, mock_get):
        """Test text generation via Ollama."""
        mock_get.return_value = Mock(
            json=lambda: {"models": [{"name": "stablelm-zephyr:3b"}]}
        )
        mock_post.return_value = Mock(
            json=lambda: {"response": "Generated text here"}
        )
        
        backend = OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")
        result = backend.generate("test prompt")
        
        assert result == "Generated text here"
        mock_post.assert_called_once()

    @patch("app.model_backend.requests.get")
    @patch("app.model_backend.requests.post")
    def test_ollama_generate_with_parameters(self, mock_post, mock_get):
        """Test generation with custom parameters."""
        mock_get.return_value = Mock(
            json=lambda: {"models": [{"name": "stablelm-zephyr:3b"}]}
        )
        mock_post.return_value = Mock(
            json=lambda: {"response": "Generated text"}
        )
        
        backend = OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")
        result = backend.generate(
            "test",
            temperature=0.5,
            top_p=0.8,
            max_new_tokens=200,
        )
        
        # Check that parameters were passed
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        assert payload["options"]["temperature"] == 0.5
        assert payload["options"]["top_p"] == 0.8
        assert payload["options"]["num_predict"] == 200

    @patch("app.model_backend.requests.get")
    def test_ollama_get_token_count(self, mock_get):
        """Test token counting."""
        mock_get.return_value = Mock(
            json=lambda: {"models": [{"name": "stablelm-zephyr:3b"}]}
        )
        
        backend = OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")
        
        # Token count should be estimated from text length
        token_count = backend.get_token_count("This is a test")
        assert isinstance(token_count, int)
        assert token_count > 0

    @patch("app.model_backend.requests.get")
    def test_ollama_base_url_normalization(self, mock_get):
        """Test that base URL has trailing slash removed."""
        mock_get.return_value = Mock(
            json=lambda: {"models": [{"name": "stablelm-zephyr:3b"}]}
        )
        
        backend = OllamaBackend("http://localhost:11434/", "stablelm-zephyr:3b")
        assert backend.base_url == "http://localhost:11434"


class TestBackendAbstraction:
    """Tests for backend abstraction and interface."""

    def test_backend_interface_has_required_methods(self):
        """Test that ModelBackend abstract class requires generate and get_token_count."""
        # Should not be able to instantiate abstract class
        with pytest.raises(TypeError):
            ModelBackend()

    @patch("app.model_backend.requests.get")
    def test_ollama_implements_backend_interface(self, mock_get):
        """Test that OllamaBackend implements ModelBackend interface."""
        mock_get.return_value = Mock(
            json=lambda: {"models": [{"name": "stablelm-zephyr:3b"}]}
        )
        
        backend = OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")
        
        # Should have required methods
        assert hasattr(backend, "generate")
        assert hasattr(backend, "get_token_count")
        assert callable(backend.generate)
        assert callable(backend.get_token_count)


class TestBackendErrorHandling:
    """Tests for error handling in backends."""

    @patch("app.model_backend.requests.get")
    @patch("app.model_backend.requests.post")
    def test_ollama_generation_error(self, mock_post, mock_get):
        """Test error handling during generation."""
        mock_get.return_value = Mock(
            json=lambda: {"models": [{"name": "stablelm-zephyr:3b"}]}
        )
        mock_post.side_effect = Exception("Network error")
        
        backend = OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")
        
        with pytest.raises(RuntimeError):
            backend.generate("test prompt")

    @patch("app.model_backend.requests.get")
    def test_ollama_token_count_error_handling(self, mock_get):
        """Test token count error handling."""
        mock_get.return_value = Mock(
            json=lambda: {"models": [{"name": "stablelm-zephyr:3b"}]}
        )
        
        backend = OllamaBackend("http://localhost:11434", "stablelm-zephyr:3b")
        
        # Should return fallback token count instead of raising error
        with patch("app.model_backend.requests.post", side_effect=Exception("Error")):
            count = backend.get_token_count("test")
            assert isinstance(count, int)
            assert count > 0  # Fallback estimate
