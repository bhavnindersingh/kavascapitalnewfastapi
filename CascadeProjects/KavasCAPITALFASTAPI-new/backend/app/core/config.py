from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Kavas Capital Options API"
    DEBUG: bool = True
    
    # Kite Connect Settings
    KITE_API_KEY: str
    KITE_API_SECRET: str
    KITE_REDIRECT_URL: str = "http://localhost:8000/api/v1/kite/callback"
    
    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kavas_capital"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # WebSocket Settings
    WS_RECONNECT_INTERVAL: int = 3000  # milliseconds
    WS_MAX_RECONNECT_ATTEMPTS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_prefix = ""  # No prefix for environment variables

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
