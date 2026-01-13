import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Central configuration for Intent-to-System AI backend
    """

    # App metadata
    APP_NAME: str = "Intent-to-System AI"
    APP_VERSION: str = "0.1"
    DEBUG: bool = True

    # Gemini
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # API
    API_PREFIX: str = "/api"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def validate_settings():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "❌ GEMINI_API_KEY not found. Please set it in the .env file."
        )
