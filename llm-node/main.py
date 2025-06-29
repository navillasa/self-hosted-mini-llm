from fastapi import FastAPI, Request
from gpt4all import GPT4All
from pathlib import Path
from pydantic import BaseModel
import os

app = FastAPI()
TEST_MODE = os.getenv("TEST_MODE", "0") == "1"

# Get model name from environment variable, with a fallback
model_name = os.getenv("MODEL_NAME", "Meta-Llama-3-8B-Instruct.Q4_0.gguf")
home_dir = Path(os.getenv("HOME", "/root"))
model_dir = home_dir / ".cache" / "gpt4all"

model = None
if not TEST_MODE:
    try:
        model = GPT4All(model_name, model_path=model_dir)
    except Exception as e:
        model = None
        print(f"Model failed to load: {e}")

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(request: GenerateRequest):
    if TEST_MODE:
        return {"response": f"Mocked response for prompt: {request.prompt}"}
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", 100)

        with model.chat_session():
            response = model.generate(prompt, max_tokens=max_tokens)

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
