# Setup Guide for AI Blog Generator

## Quick Start

### Using Ollama (Local Development)

**1. Start Ollama:**
```bash
ollama serve
```

**2. In another terminal, pull a model:**
```bash
# StableLM (recommended for beginners)
ollama pull stablelm-zephyr:3b

# Or choose another model: llama2, neural-chat, mistral, etc.
ollama pull llama2
```

**3. Create a `.env` file from the example:**
```bash
cp .env.example .env
```

**4. Edit `.env` to configure Ollama:**
```env
MODEL_BACKEND=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=stablelm-zephyr:3b
```

**5. Install dependencies:**
```bash
pip install -r requirements.txt
```

**6. Run the app:**
```bash
python run.py
```

The app will start on `http://localhost:5000`

---

## Environment Variables

See `.env.example` for all available configuration options:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `stablelm-zephyr:3b` | Model name in Ollama |
| `MAX_NEW_TOKENS` | `500` | Max tokens to generate |
| `GEN_TEMPERATURE` | `0.7` | Generation temperature (0-1) |
| `GEN_TOP_P` | `0.9` | Top-p sampling parameter (0-1) |
| `MAX_TOPIC_LEN` | `200` | Max topic length (chars) |
| `RATE_LIMIT_HOURLY` | `100` | Hourly request limit |
| `RATE_LIMIT_MINUTELY` | `10` | Per-minute request limit |
| `FLASK_ENV` | `development` | `development` or `production` |
| `DEBUG` | `False` | Enable Flask debug mode |

---

## Architecture

### Model Backend Abstraction

The application uses a plugin-based architecture with two model backends:

**OllamaBackend**: Calls Ollama's HTTP API
- ✓ Lighter weight (no GPU memory needed for app process)
- ✓ Easy local development
- ✓ Supports any Ollama-compatible model
- ✗ Requires separate Ollama service

**HuggingFaceBackend**: Uses transformers library
- ✓ Direct model loading
- ✓ More configuration options
- ✗ Requires GPU memory in app process
- ✗ Heavier dependencies

Switch between them by changing `MODEL_BACKEND` in your `.env` file.

---

## Troubleshooting

### "Could not connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check OLLAMA_BASE_URL is correct (default: http://localhost:11434)
- Verify model is installed: `ollama list`

### "CUDA out of memory" (HuggingFace backend)
- Reduce MAX_NEW_TOKENS in `.env`
- Use Ollama backend instead (lighter weight)
- Add swap space or use a GPU with more memory

### "Model not found"
- Pull the model: `ollama pull stablelm-zephyr-3b`
- Or change HUGGINGFACE_MODEL_NAME to another model

---

## Next Steps

- **Run tests**: See [TESTING.md](./TESTING.md)
- **Deploy**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Security**: See [SECURITY.md](../security/SECURITY.md)
