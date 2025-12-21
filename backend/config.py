from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # GitHub OAuth
    github_client_id: str
    github_client_secret: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Frontend URL
    frontend_url: str = "http://localhost:3000"

    # Rate Limiting
    rate_limit_per_minute: int = 10
    rate_limit_per_day: int = 100

    # LLM Model
    model_name: str = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
    test_mode: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
