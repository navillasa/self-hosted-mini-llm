from fastapi import FastAPI, Request
from gpt4all import GPT4All
import os

app = FastAPI()

# Load the model from local file
model_path = "models/Meta-Llama-3-8B-Instruct.Q4_0.gguf"
model = GPT4All(model_path)

@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    prompt = body.get("prompt", "")
    max_tokens = body.get("max_tokens", 256)

    with model.chat_session():
        output = model.generate(prompt, max_tokens=max_tokens)
        return {"response": output}

