import os
import time
import logging
import torch
import bleach
from flask import Flask, request, jsonify, abort
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

logging.basicConfig(level=logging.INFO)

class Config:
    """Application configuration."""
    MODEL_NAME = os.environ.get("MODEL_NAME", "stabilityai/stablelm-zephyr-3b")
    MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", 500))
    GEN_TEMPERATURE = float(os.environ.get("GEN_TEMPERATURE", 0.7))
    GEN_TOP_P = float(os.environ.get("GEN_TOP_P", 0.9))
    MAX_TOPIC_LEN = int(os.environ.get("MAX_TOPIC_LEN", 200))

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Initialize extensions ---
    Talisman(app, content_security_policy=None)
    limiter = Limiter(key_func=get_remote_address, default_limits=["20/hour", "5/minute"])
    limiter.init_app(app)

    # --- Model and tokenizer setup (run at app creation) ---
    app.logger.info(f"Loading model: {app.config['MODEL_NAME']}")
    try:
        app.tokenizer = AutoTokenizer.from_pretrained(app.config['MODEL_NAME'])
        model = AutoModelForCausalLM.from_pretrained(
            app.config['MODEL_NAME'],
            device_map="auto" if torch.cuda.is_available() else None,
            torch_dtype="auto"
        )
        app.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=app.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        app.logger.info(f"Model {app.config['MODEL_NAME']} loaded successfully (CPU mode: {not torch.cuda.is_available()}).")
    except Exception as e:
        app.logger.exception("Fatal error: Failed to load model.")
        # This will prevent the app from starting if the model can't be loaded
        raise RuntimeError(f"Could not load model {app.config['MODEL_NAME']}: {e}")

    def _generate_with_retry(prompt, gen_kwargs):
        """Internal helper to run generation with a single retry."""
        try:
            result = app.generator(prompt, **gen_kwargs)
            content = result[0].get("generated_text", "")
            # Retry if the output is empty or just an echo of the prompt
            if not content.strip() or content.strip() == prompt.strip():
                app.logger.info("Retrying generation with larger token budget...")
                gen_kwargs["max_new_tokens"] = app.config['MAX_NEW_TOKENS'] * 2
                gen_kwargs["temperature"] = min(1.0, app.config['GEN_TEMPERATURE'] + 0.2)
                result = app.generator(prompt, **gen_kwargs)
                content = result[0].get("generated_text", "")
            return content
        except Exception as e:
            app.logger.exception("Generation failed.")
            abort(500, "Generation error")

    def num_tokens(text: str) -> int:
        """Count input tokens for diagnostics"""
        try:
            return len(app.tokenizer(text)["input_ids"])
        except Exception:
            return 0

    def validate_topic(topic: str) -> bool:
        """Basic validation to avoid abuse or overly long topics."""
        if not topic or not isinstance(topic, str):
            return False
        if len(topic) > app.config['MAX_TOPIC_LEN']:
            return False
        # Use bleach to strip any dangerous tags/attributes
        if bleach.clean(topic, strip=True) != topic:
            return False
        return True

    def sanitize_output(prompt: str, content: str) -> str:
        """Remove echoed prompt and URLs from output."""
        if not content:
            return ""
        content = content.replace(prompt, "").strip()
        # Using bleach to be safe, though regex is also fine here
        content = bleach.linkify(content, callbacks=[lambda attrs, new: None])
        return content.strip()

    @app.route("/generate", methods=["POST"])
    @limiter.limit("10/minute;100/hour")
    def generate_blog():
        """Generate a 5-paragraph blog post on a given topic."""
        data = request.get_json(force=True, silent=True)
        if not data:
            return abort(400, "Invalid JSON body")

        topic = data.get("topic", "AI and cybersecurity")
        if not validate_topic(topic):
            return abort(400, "Invalid topic")

        prompt = (
            f"Write a clear, structured 5-paragraph blog post about: {topic}.\n\n"
            f"Structure: Introduction, three body sections (each with a heading), and a conclusion.\n"
            f"Tone: professional, and informative.\n"
            f"Do not repeat this prompt or include URLs from the input.\n"
        )

        start = time.time()
        gen_kwargs = {
            "max_new_tokens": app.config['MAX_NEW_TOKENS'],
            "do_sample": True,
            "temperature": app.config['GEN_TEMPERATURE'],
            "top_p": app.config['GEN_TOP_P'],
            "pad_token_id": app.tokenizer.eos_token_id,
            "return_full_text": False,
        }

        content = _generate_with_retry(prompt, gen_kwargs)
        content = sanitize_output(prompt, content)
        duration = round(time.time() - start, 2)

        return jsonify({
            "topic": topic,
            "content": content,
            "gen_seconds": duration
        })

    @app.route("/debug_tokens", methods=["POST"])
    def debug_tokens():
        """Return token count diagnostics for a given prompt."""
        data = request.get_json(force=True, silent=True)
        text = data.get("prompt", "")
        return jsonify({
            "prompt_len_tokens": num_tokens(text),
            "model_max_len": app.tokenizer.model_max_length
        })

    @app.route("/status", methods=["GET"])
    def status():
        """Simple health check for Postman/Docker testing."""
        return jsonify({"status": "ok", "message": "AI Blog Generator API is running"})

    return app

app = create_app()
if __name__ == "__main__":
    # Run app on localhost:5000
    # Note: For production, do not enable debug mode!
    app.run(host="0.0.0.0", port=5000)
