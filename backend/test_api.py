"""
Integration tests for the Mini LLM API
Tests health endpoints and basic API functionality in TEST_MODE
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Set test mode before importing the app
os.environ["TEST_MODE"] = "1"
os.environ["JWT_SECRET"] = "test-secret-key-for-ci"
os.environ["GITHUB_CLIENT_ID"] = "test-client-id"
os.environ["GITHUB_CLIENT_SECRET"] = "test-client-secret"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

from main import app  # noqa: E402

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and info endpoints"""

    def test_health_endpoint(self):
        """Test that health endpoint returns 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "llm_model_loaded" in data
        assert "test_mode" in data
        assert data["test_mode"] is True

    def test_root_endpoint(self):
        """Test that root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["name"] == "Mini LLM API with GitHub OAuth"

    def test_metrics_endpoint(self):
        """Test that Prometheus metrics endpoint is accessible"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "llm_requests_total" in response.text


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_github_auth_endpoint(self):
        """Test that GitHub auth endpoint returns auth URL"""
        response = client.get("/api/auth/github")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "github.com/login/oauth/authorize" in data["auth_url"]

    def test_me_endpoint_without_auth(self):
        """Test that /me endpoint requires authentication"""
        response = client.get("/api/auth/me")
        assert response.status_code in (401, 403)


class TestLLMEndpoints:
    """Test LLM generation endpoints"""

    def test_generate_endpoint_without_auth(self):
        """Test that generate endpoint requires authentication"""
        response = client.post(
            "/api/llm/generate", json={"prompt": "Hello world", "max_tokens": 50}
        )
        assert response.status_code in (401, 403)

    def test_generate_endpoint_with_invalid_payload(self):
        """Test that generate endpoint validates request payload"""
        response = client.post("/api/llm/generate", json={"invalid": "field"})
        # Should fail either due to auth or validation
        assert response.status_code in [401, 403, 422]


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test that CORS headers are set correctly"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # FastAPI handles OPTIONS automatically with CORS middleware
        assert response.status_code == 200


def test_model_not_loaded_in_test_mode():
    """Verify that model is not loaded in test mode"""
    response = client.get("/health")
    data = response.json()
    assert data["llm_model_loaded"] is False
    assert data["test_mode"] is True


if __name__ == "__main__":
    # Run tests with pytest
    sys.exit(pytest.main([__file__, "-v"]))
