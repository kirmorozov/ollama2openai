from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai
import os
app = FastAPI()
# Set OpenAI API key and URL
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_API_URL")
# Define a function to get the list of available models from OpenAI API
def get_models():
    response = openai.Model.list()
    models = [{"name": model.name, "description": model.description} for model in response.data]
    return models
# Define a function to generate a response to user input
def generate_response(model_name, prompt, temperature=0.7, max_tokens=2048, top_p=1.0):
    response = openai.Completion.create(
        model=model_name,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    return response.choices[0].text
# Define a route for the chat endpoint
@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data["message"]
    model_name = data.get("model")
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 2048)
    top_p = data.get("top_p", 1.0)
    if model_name:
        response = generate_response(model_name, message, temperature, max_tokens, top_p)
    else:
        # Use the first model in the list if no model is specified
        models = get_models()
        if models:
            model_name = models[0]["name"]
            response = generate_response(model_name, message, temperature, max_tokens, top_p)
        else:
            return JSONResponse(content={"error": "No models available"}, media_type="application/json")
    return JSONResponse(content={"response": response}, media_type="application/json")
# Define a route for the version endpoint
@app.get("/api/version")
async def version():
    return JSONResponse(content={"version": "1.0"}, media_type="application/json")
# Define a route for the tags endpoint
@app.get("/api/tags")
async def tags():
    models = get_models()
    return JSONResponse(content=[model["name"] for model in models], media_type="application/json")
# Define a route for the show endpoint
@app.get("/api/show")
async def show():
    return JSONResponse(content={"message": "LLaMA API is working"}, media_type="application/json")
# Define a route for the generate endpoint
@app.post("/api/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data["prompt"]
    model_name = data.get("model")
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 2048)
    top_p = data.get("top_p", 1.0)
    if model_name:
        response = generate_response(model_name, prompt, temperature, max_tokens, top_p)
    else:
        # Use the first model in the list if no model is specified
        models = get_models()
        if models:
            model_name = models[0]["name"]
            response = generate_response(model_name, prompt, temperature, max_tokens, top_p)
        else:
            return JSONResponse(content={"error": "No models available"}, media_type="application/json")
    return JSONResponse(content={"response": response}, media_type="application/json")