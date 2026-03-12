from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_URL = f"sqlite:///{BASE_DIR / 'dev.db'}"


class Settings(BaseSettings):
    app_name: str = "UK Transport Reliability API"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = DEFAULT_DB_URL

    tfl_app_id: str | None = None
    tfl_app_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()