from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class AppSettings(BaseSettings):
    # this will load settings from environment variables or an .env file if present
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    # these defaults are for local development and are used if the environment variables are not set
    SECRET: str = "abc123"
    DATABASE_HOST_MONDEYDB: str = "localhost"
    DATABASE_HOST_USERSDB: str = "localhost"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    DATABASE_PORT_MONDEYDB: int = 5432
    DATABASE_PORT_USERSDB: int = 5433
    STATIC_FILES_PATH: str = "static"
    PRIVATE_FILES_PATH: str = "private"
    HOST: str = "localhost"
    PORT: int = 8000
    SMTP_HOST: str = ""
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    RELOAD: bool = True
    LOG_LEVEL: str = "debug"
    COOKIE_SECURE: bool = False
    STATS_CRONTAB: str = "0 3 * * mon"
    DEEPL_API_KEY: str = ""
    MONDEY_HOST: str = "mondey.de"
    E2E_TEST_USER_SQL_FILES: str = ""
    E2E_TEST_MONDEY_SQL_FILES: str = ""
    MAX_CHILD_AGE_MONTHS: int = 72


app_settings = AppSettings()
