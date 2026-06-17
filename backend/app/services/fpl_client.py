"""Async client for the official Fantasy Premier League API.

Wraps the upstream API with a small in-memory TTL cache so we avoid hammering
it on every request, and turns transport failures into a typed error the API
layer can translate into a clean HTTP response.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from app.config import Settings, get_settings


class FPLClientError(RuntimeError):
    """Raised when the upstream FPL API is unreachable or returns an error."""


class FPLClient:
    """Thin async wrapper around the FPL API with per-key TTL caching."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._cache: dict[str, tuple[float, Any]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, key: str) -> asyncio.Lock:
        return self._locks.setdefault(key, asyncio.Lock())

    def _read_cache(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        stored_at, value = entry
        if time.monotonic() - stored_at > self._settings.cache_ttl_seconds:
            return None
        return value

    async def _fetch(self, path: str) -> Any:
        url = f"{self._settings.fpl_base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
                response = await client.get(url, headers={"User-Agent": "ProFantasyAI/1.0"})
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:  # covers timeouts, transport and status errors
            raise FPLClientError(f"Failed to fetch '{path}' from the FPL API: {exc}") from exc

    async def _get_cached_or_fetch(self, key: str, path: str) -> Any:
        cached = self._read_cache(key)
        if cached is not None:
            return cached
        async with self._lock_for(key):
            # Re-check inside the lock to avoid a stampede of concurrent fetches.
            cached = self._read_cache(key)
            if cached is not None:
                return cached
            value = await self._fetch(path)
            self._cache[key] = (time.monotonic(), value)
            return value

    async def get_bootstrap(self) -> dict[str, Any]:
        """Return the FPL ``bootstrap-static`` payload (players, teams, positions)."""
        return await self._get_cached_or_fetch("bootstrap-static", "bootstrap-static/")


_client: FPLClient | None = None


def get_fpl_client() -> FPLClient:
    """FastAPI dependency returning a process-wide singleton client."""
    global _client
    if _client is None:
        _client = FPLClient()
    return _client
