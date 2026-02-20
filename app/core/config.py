import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    app_env: str = os.getenv("APP_ENV", "dev")

settings = Settings()