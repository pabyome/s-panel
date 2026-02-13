from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "s-panel"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis_to_a_secure_random_string_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    ENVIRONMENT: str = "development"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str | None = None
    REDIS_PASS: str | None = None
    REDIS_DB: int = 0

    # Docker Registry
    DOCKER_REGISTRY: str = "127.0.0.1:5001"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
