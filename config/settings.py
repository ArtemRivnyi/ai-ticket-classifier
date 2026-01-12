"""Pydantic-based configuration management for the AI Ticket Classifier."""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration loaded from environment variables and .env file."""

    # Core secrets
    MASTER_API_KEY: str = Field(
        ..., description="Master API key for privileged automation"
    )
    SECRET_KEY: str = Field(..., description="Flask secret / JWT signing seed")

    # Providers
    GEMINI_API_KEY: Optional[str] = Field(None, description="Google Gemini API key")
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")

    # Optional services
    REDIS_URL: str = Field(
        "redis://redis:6379/0",
        description="Redis connection string used for caching and rate limiting",
    )
    DATABASE_URL: Optional[str] = Field(None, description="SQLAlchemy database URL")
    PROMETHEUS_PUSHGATEWAY: Optional[HttpUrl] = Field(
        None, description="Optional Prometheus Pushgateway endpoint"
    )
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN for error tracking")

    # Runtime behavior
    ALLOWED_ORIGINS: str = Field(
        "*", description="Comma-separated list of allowed origins"
    )
    ENV: str = Field("production", description="Runtime environment name")
    LOG_LEVEL: str = Field("INFO", description="Structlog log level")
    FORCE_HTTPS: bool = Field(
        False, description="Force HTTPS-only traffic when enabled"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    def cors_origins_list(self) -> List[str]:
        """Return sanitized list of configured CORS origins."""
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance to avoid re-parsing environment variables."""
    return Settings()
