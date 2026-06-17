"""Shared pytest fixtures.

We synthesise a realistic ``bootstrap-static`` payload so the entire test suite
runs fully offline, with no dependency on the live FPL API.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.fpl_client import FPLClientError, get_fpl_client

ELEMENT_TYPES = [
    {"id": 1, "singular_name_short": "GKP"},
    {"id": 2, "singular_name_short": "DEF"},
    {"id": 3, "singular_name_short": "MID"},
    {"id": 4, "singular_name_short": "FWD"},
]

# Players created per club, by element_type. Spread across enough clubs that a
# valid 15-man squad (max 3 per club) is comfortably feasible.
_PLAYERS_PER_POSITION = {1: 2, 2: 3, 3: 3, 4: 2}
_NUM_CLUBS = 8


def make_bootstrap() -> dict:
    """Build a deterministic synthetic FPL bootstrap payload."""
    teams = [
        {"id": tid, "name": f"Club {tid}", "short_name": f"C{tid:02d}"}
        for tid in range(1, _NUM_CLUBS + 1)
    ]

    elements: list[dict] = []
    pid = 0
    for tid in range(1, _NUM_CLUBS + 1):
        for element_type, count in _PLAYERS_PER_POSITION.items():
            for _ in range(count):
                pid += 1
                total_points = 30 + (pid * 13) % 150  # 30..179
                now_cost = 40 + (pid * 7) % 56  # 40..95 tenths (£4.0m-£9.5m)
                elements.append(
                    {
                        "id": pid,
                        "web_name": f"Player{pid}",
                        "first_name": "First",
                        "second_name": f"Last{pid}",
                        "element_type": element_type,
                        "team": tid,
                        "now_cost": now_cost,
                        "total_points": total_points,
                        # FPL returns these as strings; the optimiser coerces them.
                        "form": str(round((pid % 9) * 0.7 + 0.3, 1)),
                        "points_per_game": str(round(total_points / 25, 1)),
                        "ict_index": str(round((pid % 17) * 1.1, 1)),
                        "selected_by_percent": str(round((pid % 40) + 0.5, 1)),
                        "minutes": 200 + (pid % 30) * 30,
                        "status": "a",
                    }
                )

    return {"teams": teams, "element_types": ELEMENT_TYPES, "elements": elements}


@pytest.fixture
def bootstrap() -> dict:
    return make_bootstrap()


class _FakeFPLClient:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    async def get_bootstrap(self) -> dict:
        return self._payload


class _FailingFPLClient:
    async def get_bootstrap(self) -> dict:
        raise FPLClientError("simulated upstream outage")


@pytest.fixture
def client(bootstrap: dict) -> Iterator[TestClient]:
    app.dependency_overrides[get_fpl_client] = lambda: _FakeFPLClient(bootstrap)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def failing_client() -> Iterator[TestClient]:
    app.dependency_overrides[get_fpl_client] = lambda: _FailingFPLClient()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
