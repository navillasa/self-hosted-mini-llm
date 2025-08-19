from fastapi import FastAPI, Request, HTTPException
from gpt4all import GPT4All
from pathlib import Path
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import os
import time
import psutil

app = FastAPI()
TEST_MODE = os.getenv("TEST_MODE", "0") == "1"

# Prometheus metrics
request_count = Counter('llm_requests_total', 'Total number of requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('llm_request_duration_seconds', 'Request duration in seconds', ['method', 'endpoint'])
inference_duration = Histogram('llm_inference_duration_seconds', 'Model inference duration in seconds')
tokens_generated = Counter('llm_tokens_generated_total', 'Total tokens generated')
model_loaded = Gauge('llm_model_loaded', 'Whether the model is loaded (1) or not (0)')
cpu_usage = Gauge('llm_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('llm_memory_usage_bytes', 'Memory usage in bytes')

# Get model name from environment variable, with a fallback
model_name = os.getenv("MODEL_NAME", "Meta-Llama-3-8B-Instruct.Q4_0.gguf")
home_dir = Path(os.getenv("HOME", "/root"))
model_dir = home_dir / ".cache" / "gpt4all"

model = None
if not TEST_MODE:
    try:
        model = GPT4All(model_name, model_path=model_dir)
        model_loaded.set(1)
    except Exception as e:
        model = None
        model_loaded.set(0)
        print(f"Model failed to load: {e}")
else:
    model_loaded.set(0)  # Test mode, no real model

# Middleware to track request metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Update system metrics
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().used)
    
    response = await call_next(request)
    
    # Record request metrics
    duration = time.time() - start_time
    request_duration.labels(method=request.method, endpoint=request.url.path).observe(duration)
    request_count.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    
    return response

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

@app.post("/generate")
async def generate(request: GenerateRequest):
    if TEST_MODE:
        tokens_generated.inc(len("Mocked response for prompt: ") + len(request.prompt))
        return {"response": f"Mocked response for prompt: {request.prompt}"}
    
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        prompt = request.prompt
        inference_start = time.time()

        with model.chat_session():
            response = model.generate(prompt, max_tokens=request.max_tokens)

        # Record inference metrics
        inference_time = time.time() - inference_start
        inference_duration.observe(inference_time)
        tokens_generated.inc(len(response.split()))  # Approximate token count

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
