"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, overridable via environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ProFantasyAI"
    fpl_base_url: str = "https://fantasy.premierleague.com/api"
    cache_ttl_seconds: int = 900  # 15 minutes
    request_timeout_seconds: float = 15.0

    # Comma-separated list of origins permitted by CORS (the deployed frontend).
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (also usable as a FastAPI dependency)."""
    return Settings()
