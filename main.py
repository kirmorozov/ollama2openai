import time
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse, PlainTextResponse
import os

import openai


app = FastAPI()

client = openai.OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_URL"),
)

def filter_out_think(text):
    """
    Skip all think lines. Everything starting <think> ending </think>

    Args:
        text (str): The input text containing line breaks.
    Returns:
        str: The text after and excluding thinking section.
    """
    start_line = "<think>"
    end_line = "</think>"
    allLines = text.split("\n")
    skip = False
    filteredLines = []
    for line in allLines:
        if line.startswith(start_line):
            skip = True
        if line.startswith(end_line):
            skip = False
        if not skip:
            filteredLines.append(line)
    return "\n".join(filteredLines).strip()


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
        if response.choices is not None:
            # Return the content of the first message in the response
            return response.choices[0].message.content
        else:
            # Return an error message if the response is invalid
            if "error" in response.model_extra:
                return response.model_extra['error']["message"]
            return "No choices!!!"
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

    if "upgrade" in request.headers.keys() and "http2-settings" in request.headers:
        return Response(
            status_code=426,
            headers={"Upgrade": "HTTP/1.1"},
            content="HTTP/2 upgrade rejected"
        )

    data = await request.json()
    print(f"Question: {data}")
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

    def check_message_content(messages, prefixes, suffixes, response):
        for prefix in prefixes:
            for message in messages:
                if message['content'].startswith(prefix):
                    return filter_out_think(response), True
        for suffix in suffixes:
            for message in messages:
                if message['content'].endswith(suffix):
                    return filter_out_think(response), True
        return response, False

    skip_think_prefixes = [
        "*Original file:*",
        "Given the below code differences (diffs)"]
    skip_think_suffixes = ["please provide five improved names for this variable."]

    response, skipped_think = check_message_content(messages, skip_think_prefixes, skip_think_suffixes, response)

    res = {
        "model": model_name,
        "message": {
            "role": "assistant",
            "content": response
        },
        "done_reason": "stop",
        "done": True,
        "stream": False,
        "skipped_think": skipped_think
    }
    print(f"Answer: {response}")
    return JSONResponse(content=res, media_type="application/json")

@app.get("/api/version")
async def version():
    return JSONResponse(content={"version": "1.0"}, media_type="application/json")

@app.get("/api/tags")
async def tags():
    # Simple in-memory cache that lasts for 24 hours
    if not hasattr(tags, "cache"):
        tags.cache = {
            "result": [],
            "timestamp": 0
        }

    # Cache TTL (Time To Live) - 24 hours (86400 seconds)
    if time.time() - tags.cache["timestamp"] > 86400:
        modelsList = get_models()
        models = []
        for model in modelsList:
            model_info = {
                "name": model.id,
                "model": model.id,
                "modified_at": model.created,
                "size": 0,
                "digest": model.id,
                "details": {
                    "parent_model": "",
                    "format": "",
                    "family": "",
                    "families": [],
                    "parameter_size": "",
                    "quantization_level": ""
                }
            }
            models.append(model_info)
        tags.cache["result"] = models
        tags.cache["timestamp"] = time.time()

    return JSONResponse(content={"models": tags.cache["result"]}, media_type="application/json")

@app.post("/api/show")
async def show(reqyest: Request):
    res = {"capabilities": [
        "completion"
    ]}
    return JSONResponse(content=res, media_type="application/json")

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Ollama is running, ollama2openi really works"