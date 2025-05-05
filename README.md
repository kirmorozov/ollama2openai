# JetBrains AI Integration with Local Ollama Setup

A FastAPI-based server that provides OpenAI API compatibility using local Ollama installation.

## Installation

```bash
virtualenv venv && source venv/bin/activate && pip install -r requirements.txt
```

## Configuration

Create a `.env` file with the following environment variables:

```bash
OPENAI_API_URL="https://api.sambanova.ai/v1"
OPENAI_API_KEY="your-api-key-here"
```

## API Documentation

### Base API

`GET /`
- Description: Health check endpoint
- Response: `{"status": "ok"}`

### Models API

`GET /api/models`
- Description: List available models
- Response: `{"models": [{"name": "gpt-3.5-turbo", "description": "..."}, ...]}`
- Example: `curl http://localhost:8000/api/models`

### Chat Completion API

`POST /api/chat/completions`
- Description: Generate responses using the specified model
- Request Body:
  ```json
  {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }
  ```
- Response: `{"choices": [{"message": {"role": "assistant", "content": "..."}}]}`
- Example: `curl -X POST http://localhost:8000/api/chat/completions -H "Content-Type: application/json" -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}'`

## Project Notes

- Provides Ollama API compatibility for local development
- Pretends it is Ollama for model inference
- Supports SambaNova models through OpenAI API compatibility

## Testing

Test the endpoints using curl:

0. JetBrains AI Assistant
Point your AI Assistant to use the service:
![Settings](docs/ai.png![ai-assistant-setup.png](docs/ai-assistant-setup.png))


1. Health check:
```bash
curl http://localhost:8000/
```


2. List models:
```bash
curl http://localhost:8000/api/models
```

3. Generate response:
```bash
curl -X POST http://localhost:8000/api/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## Other attempts to do about the same
ollama-proxy