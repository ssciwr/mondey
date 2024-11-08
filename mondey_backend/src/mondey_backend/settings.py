from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class AppSettings(BaseSettings):
    # this will load settings from environment variables or an .env file if present
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # these defaults are for local development and are used if the environment variables are not set
    SECRET: str = "abc123"
    DATA_FILES_PATH: str = "data"
    DATABASE_PATH: str = "db"
    STATIC_FILES_PATH: str = "static"
    PRIVATE_FILES_PATH: str = "private"
    ENABLE_CORS: bool = True
    HOST: str = "localhost"
    PORT: int = 8000
    RELOAD: bool = True
    LOG_LEVEL: str = "debug"
    COOKIE_SECURE: bool = False


app_settings = AppSettings()
