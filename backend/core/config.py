"""
core/config.py - Application Configuration
============================================
Centralized configuration management using pydantic-settings.
Reads from environment variables and .env file with type validation.
"""

from typing import List
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.
    All settings are validated at startup; missing required values will
    raise an informative error before the app starts.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application ---
    APP_NAME: str = "repo-analyser"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- PostgreSQL ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/repo_analyser"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # --- FAISS ---
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    FAISS_DIMENSION: int = 1536  # OpenAI ada-002 embedding dimension

    # --- GitHub ---
    GITHUB_TOKEN: str = ""
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # --- AI / LLM ---
    OPENAI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    LLM_MODEL: str = "gpt-4"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # --- File System ---
    REPO_CLONE_DIR: str = "./data/repos"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Accept both JSON string lists and Python lists."""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @property
    def faiss_index_dir(self) -> Path:
        """Return FAISS index path as a Path object, creating dirs if needed."""
        path = Path(self.FAISS_INDEX_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def repo_clone_path(self) -> Path:
        """Return repo clone directory as a Path object."""
        path = Path(self.REPO_CLONE_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Singleton settings instance used throughout the application
settings = Settings()
