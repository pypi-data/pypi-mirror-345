"""Configuration settings for the markdown translator."""

import os

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()  # Load environment variables from .env


class Settings(BaseSettings):
    """Configuration settings for the markdown translator."""

    # Required OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "changeme")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # Translation settings
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "2000"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    MAX_RESPONSE_TOKENS: int = int(os.getenv("MAX_RESPONSE_TOKENS", "4000"))

    model_config = ConfigDict(
        env_file=".env",
        extra="allow",  # Allow extra fields
        case_sensitive=False,
    )
