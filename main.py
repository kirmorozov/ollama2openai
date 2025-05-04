from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import os

import openai

app = FastAPI()

client = openai.OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_URL"),
)


def get_models():
    try:
        response = client.models.list()
        return response.data
    except Exception as e:
        print(f"Error getting models: {e}")
        return []

def generate_chat_response(model_name, messages, temperature=0.7, max_tokens=2048, top_p=1.0):
    """
    Generate a chat response using the OpenAI API.

    Args:
    - model_name (str): The name of the model to use.
    - messages (list): A list of messages to send to the model.
    - temperature (float, optional): The temperature to use for the model. Defaults to 0.7.
    - max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 2048.
    - top_p (float, optional): The top-p value to use for the model. Defaults to 1.0.

    Returns:
    - str: The generated chat response.
    """
    try:
        # Create the completion request
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )

        # Check if the response is valid
        if len(response.choices) > 0:
            # Return the content of the first message in the response
            return response.choices[0].message.content
        else:
            # Return an error message if the response is invalid
            return "Invalid response from OpenAI API"
    except openai.error.AuthenticationError:
        # Handle authentication errors
        return "Authentication error: please check your OpenAI API key"
    except openai.error.APIError as e:
        # Handle API errors
        return f"API error: {e}"
    except Exception as e:
        # Handle any other exceptions
        return f"Error: {e}"

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data["messages"]
    model_name = data.get("model")
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 2048)
    top_p = data.get("top_p", 1.0)

    if model_name:
        response = generate_chat_response(model_name, messages, temperature, max_tokens, top_p)
    else:
        models = get_models()
        if models:
            model_name = models[0]["name"]
            response = generate_chat_response(model_name, messages, temperature, max_tokens, top_p)
        else:
            return JSONResponse(content={"error": "No models available"}, media_type="application/json")

    res = {
        "model": model_name,
        "message": {
            "role": "assistant",
            "content": response
        }
    }
    return JSONResponse(content=res, media_type="application/json")

@app.get("/api/version")
async def version():
    return JSONResponse(content={"version": "1.0"}, media_type="application/json")

@app.get("/api/tags")
async def tags():
    modelsList = get_models()
    models = []
    for model in modelsList:
        model_info = {
            "name": model.id,
            "model": model.id,
            "modified_at": model.created,
            "size": 0,  # OpenAI API does not provide model size
            "digest": model.id,  # OpenAI API does not provide model digest
            "details": {
                "parent_model": "",  # OpenAI API does not provide parent model
                "format": "",  # OpenAI API does not provide model format
                "family": "",  # OpenAI API does not provide model family
                "families": [],  # OpenAI API does not provide model families
                "parameter_size": "",  # OpenAI API does not provide model parameter size
                "quantization_level": ""  # OpenAI API does not provide model quantization level
            }
        }
        models.append(model_info)
    return JSONResponse(content={"models": models}, media_type="application/json")

@app.post("/api/show")
async def show(reqyest: Request):
    res = {"capabilities": [
        "completion"
    ]}
    return JSONResponse(content=res, media_type="application/json")

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Ollama is running, ollama2openai"