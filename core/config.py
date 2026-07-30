from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "YT_AI_NOTES"
    DEBUG: bool = False

    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"

    WHISPER_COMPUTE_TYPE: str = "int8"

    DATABASE_URL: str = ""

    GEMINI_API_KEY: str = ""

    SESSION_SECRET_KEY: str = "session-secret"
    SESSION_COOKIE_NAME: str = "session"
    SESSION_COOKIE_SECURE: bool = False

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_CALLBACK_URL: str = ""

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
