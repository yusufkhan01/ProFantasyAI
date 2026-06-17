"""Tests for the FPL client's caching and error handling."""

from __future__ import annotations

import pytest

from app.services.fpl_client import FPLClient, FPLClientError


async def test_client_caches_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    client = FPLClient()
    calls = {"count": 0}

    async def fake_fetch(path: str) -> dict:
        calls["count"] += 1
        return {"path": path, "ok": True}

    monkeypatch.setattr(client, "_fetch", fake_fetch)

    first = await client.get_bootstrap()
    second = await client.get_bootstrap()

    assert first == second == {"path": "bootstrap-static/", "ok": True}
    assert calls["count"] == 1  # second call served from cache


async def test_client_propagates_fetch_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    client = FPLClient()

    async def boom(path: str) -> dict:
        raise FPLClientError("upstream down")

    monkeypatch.setattr(client, "_fetch", boom)

    with pytest.raises(FPLClientError):
        await client.get_bootstrap()
