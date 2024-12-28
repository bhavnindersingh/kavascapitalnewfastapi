from pydantic_settings import BaseSettings
from functools import lru_cache

class KiteSettings(BaseSettings):
    api_key: str = ""
    api_secret: str = ""
    redirect_url: str = "http://localhost:8000/api/v1/kite/callback"
    access_token: str = ""
    
    class Config:
        env_file = ".env"
        env_prefix = "KITE_"

@lru_cache()
def get_kite_settings() -> KiteSettings:
    return KiteSettings()
