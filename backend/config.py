from pydantic_settings import BaseSettings


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
    llm_model_name: str = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    test_mode: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
