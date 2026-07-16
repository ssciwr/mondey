from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class AppSettings(BaseSettings):
    # this will load settings from environment variables or an .env file if present
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # these defaults are for local development and are used if the environment variables are not set
    SECRET: str = "dev-only-insecure-secret-change-me"
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
    MIN_PASSWORD_LENGTH: int = 12
    # How long an account activation link stays valid. Long enough that a user
    # who doesn't read their email straight away can still use it.
    VERIFICATION_TOKEN_LIFETIME_SECONDS: int = 24 * 3600
    MILESTONE_MIN_ANSWERS_FOR_CURVE_FIT: int = 100
    SESSION_IDLE_TIMEOUT_SECONDS: int = 3600
    SESSION_ABSOLUTE_TIMEOUT_SECONDS: int = 8 * 3600
    SESSION_TOUCH_INTERVAL_SECONDS: int = 300
    SESSION_WARNING_SECONDS: int = 300

    @model_validator(mode="after")
    def validate_secret(self):
        min_secret_length = 20
        if len(self.SECRET) < min_secret_length:
            raise ValueError(
                f"SECRET must be at least {min_secret_length} characters long. "
                "Set it to a long random string (see DEPLOYMENT.md)."
            )
        return self

    @model_validator(mode="after")
    def validate_min_password_length(self):
        lowest_allowed_min_password_length = 8
        if lowest_allowed_min_password_length > self.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"MIN_PASSWORD_LENGTH must be at least {lowest_allowed_min_password_length}"
            )
        return self

    @model_validator(mode="after")
    def validate_session_timeouts(self):
        if self.SESSION_IDLE_TIMEOUT_SECONDS <= 0:
            raise ValueError("SESSION_IDLE_TIMEOUT_SECONDS must be positive")
        if self.SESSION_ABSOLUTE_TIMEOUT_SECONDS < self.SESSION_IDLE_TIMEOUT_SECONDS:
            raise ValueError(
                "SESSION_ABSOLUTE_TIMEOUT_SECONDS must be at least the idle timeout"
            )
        if self.SESSION_TOUCH_INTERVAL_SECONDS <= 0:
            raise ValueError("SESSION_TOUCH_INTERVAL_SECONDS must be positive")
        if self.SESSION_WARNING_SECONDS <= 0:
            raise ValueError("SESSION_WARNING_SECONDS must be positive")
        return self


app_settings = AppSettings()
