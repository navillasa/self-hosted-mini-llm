from fastapi import FastAPI, Request
from gpt4all import GPT4All
import os
from pathlib import Path

app = FastAPI()

# Get model name from environment variable, with a fallback
model_name = os.getenv("MODEL_NAME", "Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Expand `~` to absolute path
model_path = Path("~/.cache/gpt4all") / model_name
model_path = model_path.expanduser()

# Load the model
model = GPT4All(model_name, model_path=model_path)

@app.post("/generate")
async def generate_text(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    max_tokens = data.get("max_tokens", 100)

    with model.chat_session():
        response = model.generate(prompt, max_tokens=max_tokens)
    
    return {"response": response}
