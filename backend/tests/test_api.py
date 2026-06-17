"""Integration tests for the HTTP API (FPL client mocked via dependency override)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.constants import SQUAD_SIZE


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"]


def test_optimal_team_endpoint(client: TestClient) -> None:
    response = client.get("/api/optimal-team")
    assert response.status_code == 200
    body = response.json()
    assert len(body["starting_xi"]) == 11
    assert len(body["bench"]) == 4
    assert len(body["squad"]) == SQUAD_SIZE
    assert body["captain_id"]
    assert "formation" in body["metrics"]
    assert body["is_projection"] is False
    assert body["season"] == "2025-26"
    # Each player carries the stable club code (sourced from teams[].code, not id)
    # that the frontend uses to render crest images.
    assert all(player["team_code"] >= 100 for player in body["squad"])


def test_optimal_team_predicted_season(client: TestClient) -> None:
    response = client.get("/api/optimal-team", params={"season": "2026-27"})
    assert response.status_code == 200
    body = response.json()
    assert body["season"] == "2026-27"
    assert body["is_projection"] is True
    assert body["metrics"]["squad_total_points"] > 0


def test_optimal_team_rejects_invalid_season(client: TestClient) -> None:
    response = client.get("/api/optimal-team", params={"season": "1999-00"})
    assert response.status_code == 422


def test_players_endpoint_with_filters(client: TestClient) -> None:
    response = client.get("/api/players", params={"limit": 7, "position": "DEF"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 7
    assert all(player["position"] == "DEF" for player in body)


def test_players_endpoint_rejects_invalid_position(client: TestClient) -> None:
    response = client.get("/api/players", params={"position": "XYZ"})
    assert response.status_code == 422


def test_optimal_team_handles_upstream_failure(failing_client: TestClient) -> None:
    response = failing_client.get("/api/optimal-team")
    assert response.status_code == 502
