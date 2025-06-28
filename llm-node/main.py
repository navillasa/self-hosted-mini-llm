from fastapi import FastAPI, Request
from gpt4all import GPT4All
from pathlib import Path
import os

TEST_MODE = os.getenv("TEST_MODE", "0") == "1"

app = FastAPI()

# Get model name from environment variable, with a fallback
model_name = os.getenv("MODEL_NAME", "Meta-Llama-3-8B-Instruct.Q4_0.gguf")

home_dir = Path(os.getenv("HOME", "/root"))

# Directory where models are stored
model_dir = home_dir / ".cache" / "gpt4all"

# Load the model
model = GPT4All(model_name, model_path=model_dir)

@app.post("/generate")
async def generate_text(request: Request):
    if TEST_MODE:
        return {"response": "mocked response"}

    data = await request.json()
    prompt = data.get("prompt", "")
    max_tokens = data.get("max_tokens", 100)

    with model.chat_session():
        response = model.generate(prompt, max_tokens=max_tokens)

    return {"response": response}

