from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response, RedirectResponse
import os
import time
import psutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

from config import settings
from auth import exchange_github_code_for_token, get_github_user, create_jwt_token, verify_jwt_token
from rate_limiter import rate_limiter

# Conditionally import Llama only when not in test mode
if not settings.test_mode:
    from llama_cpp import Llama

app = FastAPI(title="Mini LLM with GitHub OAuth")

# Thread pool for async LLM inference
executor = ThreadPoolExecutor(max_workers=2)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
request_count = Counter('llm_requests_total', 'Total number of requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('llm_request_duration_seconds', 'Request duration in seconds', ['method', 'endpoint'])
inference_duration = Histogram('llm_inference_duration_seconds', 'Model inference duration in seconds')
tokens_generated = Counter('llm_tokens_generated_total', 'Total tokens generated')
llm_model_loaded = Gauge('llm_model_loaded', 'Whether the model is loaded (1) or not (0)')
cpu_usage = Gauge('llm_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('llm_memory_usage_bytes', 'Memory usage in bytes')
auth_requests = Counter('llm_auth_requests_total', 'Total authentication requests', ['provider', 'status'])
rate_limit_hits = Counter('llm_rate_limit_hits_total', 'Total rate limit hits', ['limit_type'])

def get_model_dir() -> Path:
    # Prefer XDG_CACHE_HOME if set, else HOME/.cache, else /tmp/.cache
    xdg = os.getenv("XDG_CACHE_HOME")
    if xdg:
        base = Path(xdg)
    else:
        home = os.getenv("HOME")
        base = Path(home) / ".cache" if home else Path("/tmp") / ".cache"
    return base / "gpt4all"

llm_model_dir = get_model_dir()
llm_model_dir.mkdir(parents=True, exist_ok=True)

llm_model = None
if not settings.test_mode:
    try:
        llm_model_path = llm_model_dir / settings.llm_model_name
        llm_model = Llama(model_path=str(llm_model_path), n_ctx=2048, n_threads=4)
        llm_model_loaded.set(1)
        print(f"✅ Model loaded: {settings.llm_model_name}")
    except Exception as e:
        llm_model = None
        llm_model_loaded.set(0)
        print(f"❌ Model failed to load: {e}")
else:
    llm_model_loaded.set(0)
    print("🧪 Test mode enabled - no real model loaded")

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


# ============================================================================
# Auth Endpoints
# ============================================================================

@app.get("/api/auth/github")
async def github_auth():
    """Redirect to GitHub OAuth"""
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&scope=read:user user:email"
    )
    return {"auth_url": github_auth_url}


@app.get("/api/auth/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback"""
    try:
        # Exchange code for access token
        token_data = await exchange_github_code_for_token(code)
        access_token = token_data.get("access_token")

        if not access_token:
            auth_requests.labels(provider="github", status="failed").inc()
            raise HTTPException(status_code=400, detail="Failed to get access token")

        # Get user info from GitHub
        user_info = await get_github_user(access_token)

        # Create JWT
        jwt_token = create_jwt_token(user_info)

        auth_requests.labels(provider="github", status="success").inc()

        # Redirect to frontend with token
        redirect_url = f"{settings.frontend_url}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=redirect_url)

    except HTTPException:
        raise
    except Exception as e:
        auth_requests.labels(provider="github", status="error").inc()
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/api/auth/me")
async def get_current_user(user_data: dict = Depends(verify_jwt_token)):
    """Get current user info and usage stats"""
    user_id = user_data["sub"]
    usage_stats = rate_limiter.get_usage_stats(user_id)

    return {
        "user": {
            "id": user_data["sub"],
            "username": user_data["username"],
            "avatar_url": user_data.get("avatar_url"),
        },
        "usage": usage_stats
    }


# ============================================================================
# LLM Endpoints
# ============================================================================

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100


@app.post("/api/llm/generate")
async def generate(request: GenerateRequest, user_data: dict = Depends(verify_jwt_token)):
    """Generate LLM response (requires authentication)"""
    user_id = user_data["sub"]
    username = user_data["username"]

    # Check rate limits
    try:
        usage_stats = rate_limiter.check_rate_limit(user_id)
    except HTTPException as e:
        # Log rate limit hit
        if "per_minute" in str(e.detail):
            rate_limit_hits.labels(limit_type="per_minute").inc()
        elif "per_day" in str(e.detail):
            rate_limit_hits.labels(limit_type="per_day").inc()
        raise

    # Test mode
    if settings.test_mode:
        response_text = f"[TEST MODE] Mock response for: {request.prompt[:50]}..."
        tokens_generated.inc(len(response_text.split()))
        return {
            "response": response_text,
            "usage": usage_stats,
            "user": username
        }

    # Check if model is loaded
    if not llm_model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Generate response
    try:
        inference_start = time.time()

        # Run LLM inference in background thread to not block event loop
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            executor,
            lambda: llm_model(
                request.prompt,
                max_tokens=request.max_tokens,
                temperature=0.7,
                stop=["</s>", "Human:", "User:"]
            )
        )
        response_text = output['choices'][0]['text']

        # Record metrics
        inference_time = time.time() - inference_start
        inference_duration.observe(inference_time)
        tokens_generated.inc(len(response_text.split()))

        return {
            "response": response_text,
            "usage": usage_stats,
            "inference_time_seconds": round(inference_time, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# ============================================================================
# Health & Metrics
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "llm_model_loaded": llm_model is not None,
        "test_mode": settings.test_mode
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Mini LLM API with GitHub OAuth",
        "version": "1.0.0",
        "auth": "GitHub OAuth 2.0",
        "endpoints": {
            "auth": "/api/auth/github",
            "generate": "/api/llm/generate (requires auth)",
            "user_info": "/api/auth/me (requires auth)",
            "health": "/health",
            "metrics": "/metrics"
        }
    }
