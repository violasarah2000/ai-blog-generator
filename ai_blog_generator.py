import os
import re
import time
import logging
import torch
from flask import Flask, request, jsonify, abort
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from flask_limiter import Limiter   # enforce rates limits to reduce abuse
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman  # for secure headers HSTS, CSP...

# Initialize Flask app
app = Flask(__name__)
Talisman(app, content_security_policy=None) 
limiter = Limiter(app, key_func=get_remote_address, default_limits=["20/hour", "5/minute"])
logging.basicConfig(level=logging.INFO)

# Config via env vars
MODEL_NAME = os.environ.get("MODEL_NAME", "stabilityai/stablelm-zephyr-3b")
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", 500))
GEN_TEMPERATURE = float(os.environ.get("GEN_TEMPERATURE", 0.7))
GEN_TOP_P = float(os.environ.get("GEN_TOP_P", 0.9))
MAX_TOPIC_LEN = int(os.environ.get("MAX_TOPIC_LEN", "200"))

# --- Model and tokenizer setup ---
app.logger.info(f"Loading model: {MODEL_NAME}")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto" if torch.cuda.is_available() else None,
        torch_dtype="auto"  # uses bfloat16/fp16 if available, otherwise fp32
    )

    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1  # -1 = CPU mode
    )

    app.logger.info(f"Model {MODEL_NAME} loaded successfully (CPU mode: {not torch.cuda.is_available()}).")

except Exception as e:
    app.logger.exception("Failed to load model.")
    raise RuntimeError(f"Could not load model {MODEL_NAME}: {e}")

def num_tokens(text: str) -> int:
    """Count input tokens for diagnostics"""
    try:
        return len(tokenizer(text)["input_ids"])
    except Exception:
        return 0

def validate_topic(topic: str) -> bool:
    """Basic validation to avoid abuse or overly long topics."""
    if not topic or not isinstance(topic, str):
        return False
    if len(topic) > MAX_TOPIC_LEN:
        return False
    if re.search(r"[<>;{}]", topic):  # basic injection filter
        return False
    return True

def sanitize_output(prompt: str, content: str) -> str:
    """Remove echoed prompt and URLs from output."""
    if not content:
        return ""
    content = content.replace(prompt, "").strip()
    content = re.sub(r"https?://\S+", "[URL removed]", content)
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
        "max_new_tokens": MAX_NEW_TOKENS,
        "do_sample": True,
        "temperature": GEN_TEMPERATURE,
        "top_p": GEN_TOP_P,
        "pad_token_id": tokenizer.eos_token_id,
        "return_full_text": False,
    }

    try:
        result = generator(prompt, **gen_kwargs)
        content = result[0].get("generated_text", "")
        # retry logic if output = prompt or blank
        if not content.strip() or content.strip() == prompt.strip():
            app.logger.info("Retrying generation with larger token budget...")
            gen_kwargs["max_new_tokens"] = MAX_NEW_TOKENS * 2
            gen_kwargs["temperature"] = min(1.0, GEN_TEMPERATURE + 0.2)
            result = generator(prompt, **gen_kwargs)
            content = result[0].get("generated_text", "")
    except Exception as e:
        app.logger.exception("Generation failed.")
        return abort(500, "generation error")

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
        "model_max_len": tokenizer.model_max_length
    })


@app.route("/status", methods=["GET"])
def status():
    """Simple health check for Postman/Docker testing."""
    return jsonify({"status": "ok", "message": "AI Blog Generator API is running"})

if __name__ == "__main__":
    # Run app on localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)

# no __main__ debug server in production; use gunicorn to run
