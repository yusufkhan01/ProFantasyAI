"""Unit tests for the upcoming-season projection model."""

from __future__ import annotations

from app.services.optimizer import _parse
from app.services.projection import compute_projections


def test_projections_are_non_negative(bootstrap: dict) -> None:
    candidates, _ = _parse(bootstrap)
    compute_projections(candidates)
    assert candidates
    assert all(c.projected_points >= 0 for c in candidates)


def test_players_without_minutes_project_zero(bootstrap: dict) -> None:
    candidates, _ = _parse(bootstrap)
    candidates[0].minutes = 0
    compute_projections(candidates)
    assert candidates[0].projected_points == 0.0


def test_more_minutes_and_points_projects_higher(bootstrap: dict) -> None:
    candidates, _ = _parse(bootstrap)
    # Two identical-position players; one clearly out-produces the other.
    same_pos = [c for c in candidates if c.position == "MID"][:2]
    weak, strong = same_pos
    weak.minutes, weak.total_points = 1800, 60
    weak.xg90 = weak.xa90 = 0.0
    strong.minutes, strong.total_points = 3200, 220
    strong.xg90, strong.xa90 = 0.6, 0.3

    compute_projections(candidates)
    assert strong.projected_points > weak.projected_points
