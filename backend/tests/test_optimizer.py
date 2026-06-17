"""Unit tests for the squad optimisation logic."""

from __future__ import annotations

import pytest

from app.core.constants import (
    BUDGET,
    COST_DIVISOR,
    MAX_PLAYERS_PER_CLUB,
    SQUAD_REQUIREMENTS,
    SQUAD_SIZE,
)
from app.services.optimizer import (
    OptimizerError,
    _parse,
    _score,
    build_optimal_team,
    value_leaders,
)


def test_scores_are_within_bounds(bootstrap: dict) -> None:
    candidates, _ = _parse(bootstrap)
    _score(candidates)
    assert candidates
    assert all(0.0 <= c.value_score <= 100.0 for c in candidates)


def test_build_optimal_team_respects_constraints(bootstrap: dict) -> None:
    result = build_optimal_team(bootstrap)

    assert len(result.squad) == SQUAD_SIZE

    counts = dict.fromkeys(SQUAD_REQUIREMENTS, 0)
    for player in result.squad:
        counts[player.position] += 1
    assert counts == SQUAD_REQUIREMENTS

    assert result.metrics.total_cost <= BUDGET / COST_DIVISOR + 1e-6
    assert result.metrics.budget_remaining >= -1e-6

    club_counts: dict[int, int] = {}
    for player in result.squad:
        club_counts[player.team_id] = club_counts.get(player.team_id, 0) + 1
    assert max(club_counts.values()) <= MAX_PLAYERS_PER_CLUB


def test_starting_xi_and_formation_are_valid(bootstrap: dict) -> None:
    result = build_optimal_team(bootstrap)

    assert len(result.starting_xi) == 11
    assert len(result.bench) == 4

    positions = [p.position for p in result.starting_xi]
    assert positions.count("GK") == 1
    defenders = positions.count("DEF")
    midfielders = positions.count("MID")
    forwards = positions.count("FWD")
    assert 3 <= defenders <= 5
    assert 2 <= midfielders <= 5
    assert 1 <= forwards <= 3
    assert defenders + midfielders + forwards == 10
    assert result.metrics.formation == f"{defenders}-{midfielders}-{forwards}"


def test_captain_is_highest_value_starter(bootstrap: dict) -> None:
    result = build_optimal_team(bootstrap)
    captain = next(p for p in result.starting_xi if p.is_captain)
    assert captain.id == result.captain_id
    assert captain.value_score == max(p.value_score for p in result.starting_xi)


def test_eligibility_excludes_unavailable_players(bootstrap: dict) -> None:
    top_scorer = max(bootstrap["elements"], key=lambda e: e["total_points"])
    top_scorer["status"] = "i"  # injured
    top_scorer["minutes"] = 0

    result = build_optimal_team(bootstrap)
    assert all(p.id != top_scorer["id"] for p in result.squad)


def test_value_leaders_are_sorted_and_limited(bootstrap: dict) -> None:
    leaders = value_leaders(bootstrap, limit=5)
    assert len(leaders) == 5
    scores = [p.value_score for p in leaders]
    assert scores == sorted(scores, reverse=True)


def test_value_leaders_respect_position_filter(bootstrap: dict) -> None:
    midfielders = value_leaders(bootstrap, limit=10, position="MID")
    assert midfielders
    assert all(p.position == "MID" for p in midfielders)


def test_build_raises_when_squad_is_infeasible() -> None:
    tiny = {
        "teams": [{"id": 1, "name": "Club 1", "short_name": "C01"}],
        "element_types": [],
        "elements": [
            {
                "id": 1,
                "web_name": "Solo",
                "first_name": "S",
                "second_name": "Olo",
                "element_type": 1,
                "team": 1,
                "now_cost": 50,
                "total_points": 100,
                "form": "5.0",
                "points_per_game": "4.0",
                "ict_index": "10.0",
                "selected_by_percent": "10.0",
                "minutes": 900,
                "status": "a",
            }
        ],
    }
    with pytest.raises(OptimizerError):
        build_optimal_team(tiny)
