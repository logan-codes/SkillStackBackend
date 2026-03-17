# SECRET_KEY, token expiry settings
# core/config.py

from pydantic_settings import BaseSettings  # reads .env automatically


class Settings(BaseSettings):

    # --- Database ---
    DATABASE_URL: str                        # e.g. postgresql://user:pass@localhost/dbname

    # --- JWT ---
    SECRET_KEY: str                          # long random string, NEVER share this
    ALGORITHM: str = "HS256"                 # how we sign the token, HS256 is standard
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60    # token dies after 60 mins, user must re-login

    # --- App ---
    APP_NAME: str = "SkillStack API"

    class Config:
        env_file = ".env"                    # tells pydantic: read from .env file


# This is the ONE instance every other file will import
# import like: from core.config import settings
settings = Settings()