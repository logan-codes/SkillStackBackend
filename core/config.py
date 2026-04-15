# Configuration settings from .env
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_NAME: str = "SkillStack API"

    # Extra fields that might be in .env
    SUPABASE_DATABASE_URL: Optional[str] = None
    LOCAL_DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields in .env


settings = Settings()
