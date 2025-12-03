"""
Flask application factory for AI Blog Generator.

Handles request routing, rate limiting, and security features.
"""

import os
import time
import logging
from flask import Flask, request, jsonify, abort, render_template_string, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from app.config import Config, DevelopmentConfig, ProductionConfig
from app.backends import init_model_backend
from app.validators import InputValidator, ValidationError
from app.generation import GenerationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Simple HTML UI template
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Blog Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        button {
            flex: 1;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-generate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-generate:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-generate:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-clear {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-clear:hover {
            background: #e0e0e0;
        }
        
        #loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        #result {
            display: none;
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #eee;
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .result-header h2 {
            color: #333;
            font-size: 18px;
        }
        
        .result-meta {
            font-size: 12px;
            color: #999;
        }
        
        .result-content {
            color: #555;
            line-height: 1.8;
            font-size: 14px;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 6px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            border: 1px solid #fcc;
        }
        
        .success {
            background: #efe;
            color: #3c3;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #cfc;
        }
        
        .char-count {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 22px;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Blog Generator</h1>
        <p class="subtitle">Generate 5-paragraph blog posts with AI • Powered by Ollama (Local)</p>
        
        <form id="blogForm">
            <div class="form-group">
                <label for="topic">Topic</label>
                <input 
                    type="text" 
                    id="topic" 
                    placeholder="e.g., Artificial Intelligence and Cybersecurity"
                    maxlength="200"
                    required
                >
                <div class="char-count"><span id="charCount">0</span>/200 characters</div>
            </div>
            
            <div class="button-group">
                <button type="submit" class="btn-generate" id="generateBtn">Generate Blog Post</button>
                <button type="reset" class="btn-clear">Clear</button>
            </div>
        </form>
        
        <div id="loading">
            <div class="spinner"></div>
            <p>Generating your blog post... This may take 10-30 seconds.</p>
        </div>
        
        <div id="result"></div>
    </div>
    
    <script>
        const form = document.getElementById('blogForm');
        const topicInput = document.getElementById('topic');
        const generateBtn = document.getElementById('generateBtn');
        const loadingDiv = document.getElementById('loading');
        const resultDiv = document.getElementById('result');
        const charCountSpan = document.getElementById('charCount');
        
        // Update character count
        topicInput.addEventListener('input', (e) => {
            charCountSpan.textContent = e.target.value.length;
        });
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const topic = topicInput.value.trim();
            if (!topic) {
                showError('Please enter a topic');
                return;
            }
            
            generateBtn.disabled = true;
            loadingDiv.style.display = 'block';
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ topic })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.description || 'Failed to generate blog post');
                }
                
                showResult(data);
            } catch (error) {
                showError(error.message || 'An error occurred while generating the blog post');
            } finally {
                generateBtn.disabled = false;
                loadingDiv.style.display = 'none';
            }
        });
        
        function showResult(data) {
            const html = `
                <div class="success">✓ Blog post generated successfully</div>
                <div class="result-header">
                    <h2>Topic: ${escapeHtml(data.topic)}</h2>
                    <div class="result-meta">Generated in ${data.gen_seconds}s</div>
                </div>
                <div class="result-content">${escapeHtml(data.content)}</div>
            `;
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        function showError(message) {
            const html = `<div class="error">✗ Error: ${escapeHtml(message)}</div>`;
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""


def create_app(config_class=None):
    """Create and configure the Flask application."""
    if config_class is None:
        config_class = (
            DevelopmentConfig
            if os.environ.get("FLASK_ENV") == "development"
            else ProductionConfig
        )

    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Initialize extensions ---
    # Only enable Talisman in production (not in development or testing)
    if app.config.get("FLASK_ENV") == "production":
        Talisman(app, content_security_policy=None)
    
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[
            f"{app.config['RATE_LIMIT_HOURLY']}/hour",
            f"{app.config['RATE_LIMIT_MINUTELY']}/minute",
        ],
    )
    limiter.init_app(app)

    @app.before_request
    def log_request():
        """Debug logging for all requests."""
        logger.debug(f"Request to {request.path}")

    # --- Validate configuration ---
    config_class.validate()

    # --- Initialize model backend ---
    app.model_backend = init_model_backend(app.config)

    # --- Initialize generation service ---
    gen_service = GenerationService(app.model_backend, app.config)

    def validate_topic(topic: str) -> str:
        """Validate topic using centralized validator."""
        try:
            return InputValidator.validate_topic(topic)
        except ValidationError as e:
            abort(400, str(e))

    @app.route("/", methods=["GET"])
    def index():
        """Serve the web UI for blog generation."""
        return Response(UI_TEMPLATE, mimetype="text/html")

    @app.route("/generate", methods=["POST"])
    @limiter.limit("10/minute;100/hour")
    def generate_blog():
        """Generate a 5-paragraph blog post on a given topic."""
        data = request.get_json(force=True, silent=True)
        if data is None:
            return abort(400, "Invalid JSON body")

        topic = data.get("topic", "AI and cybersecurity")
        topic = validate_topic(topic)

        prompt = (
            f"Write a clear, structured 5-paragraph blog post about: {topic}.\n\n"
            f"Structure: Introduction, three body sections (each with a heading), and a conclusion.\n"
            f"Tone: professional, and informative.\n"
            f"Do not repeat this prompt or include URLs from the input.\n"
        )

        start = time.time()
        gen_kwargs = {
            "max_new_tokens": app.config["MAX_NEW_TOKENS"],
            "temperature": app.config["GEN_TEMPERATURE"],
            "top_p": app.config["GEN_TOP_P"],
        }

        content = gen_service.generate_with_retry(prompt, gen_kwargs)
        content = InputValidator.sanitize_output(prompt, content)
        duration = round(time.time() - start, 2)

        return jsonify({"topic": topic, "content": content, "gen_seconds": duration})

    @app.route("/debug_tokens", methods=["POST"])
    def debug_tokens():
        """Return token count diagnostics for a given prompt."""
        data = request.get_json(force=True, silent=True)
        if data is None:
            return abort(400, "Invalid JSON body")
        text = data.get("prompt", "")
        token_count = gen_service.get_token_count(text)
        return jsonify({"prompt_len_tokens": token_count})

    @app.route("/status", methods=["GET"])
    @limiter.exempt
    def status():
        """Simple health check for Postman/Docker testing."""
        return jsonify({"status": "ok", "message": "AI Blog Generator API is running"})

    return app


if __name__ == "__main__":
    app = create_app()
    # Run app on localhost:5000
    # Note: For production, do not enable debug mode!
    app.run(host="0.0.0.0", port=5000)
