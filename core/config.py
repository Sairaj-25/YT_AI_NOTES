from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "YT_AI_NOTES"
    DEBUG: bool

    WHISPER_MODEL_SIZE: str
    WHISPER_DEVICE: str

    WHISPER_COMPUTE_TYPE: str

    DATABASE_URL: str

    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR/".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()