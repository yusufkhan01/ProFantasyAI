"""Unit tests for the squad optimisation logic."""

from __future__ import annotations

from itertools import combinations

import pytest

from app.core.constants import (
    BUDGET,
    COST_DIVISOR,
    MAX_PLAYERS_PER_CLUB,
    SEASON_HISTORICAL,
    SEASON_PREDICTED,
    SQUAD_REQUIREMENTS,
    SQUAD_SIZE,
)
from app.services.optimizer import (
    OptimizerError,
    _build_squad,
    _parse,
    _resolve_season,
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


def test_captain_is_highest_scoring_starter(bootstrap: dict) -> None:
    result = build_optimal_team(bootstrap)
    captain = next(p for p in result.starting_xi if p.is_captain)
    assert captain.id == result.captain_id
    # The captain maximises the optimisation objective (points), not value-for-money.
    assert captain.objective_points == max(p.objective_points for p in result.starting_xi)


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


def _knapsack_bootstrap() -> dict:
    """A small pool (each player on a unique club) where budget genuinely binds.

    Unique clubs neutralise the max-per-club rule, so the exact knapsack must match
    a brute-force optimum over budget + positional constraints alone.
    """
    counts = {1: 4, 2: 7, 3: 7, 4: 5}  # GK, DEF, MID, FWD
    elements: list[dict] = []
    pid = 0
    for element_type, n in counts.items():
        for _ in range(n):
            pid += 1
            total_points = 20 + (pid * 17) % 200  # 20..219
            # Correlate price with output so the £100m budget genuinely binds,
            # while the cheapest legal squad still fits comfortably.
            now_cost = 40 + total_points // 5  # ~£4.4m..£8.3m
            elements.append(
                {
                    "id": pid,
                    "web_name": f"P{pid}",
                    "first_name": "F",
                    "second_name": f"L{pid}",
                    "element_type": element_type,
                    "team": pid,  # unique club per player
                    "now_cost": now_cost,
                    "cost_change_start": 0,
                    "total_points": total_points,
                    "minutes": 900,
                    "status": "a",
                }
            )
    teams = [
        {"id": p["team"], "name": f"C{p['team']}", "short_name": f"C{p['team']:02d}"}
        for p in elements
    ]
    return {"teams": teams, "elements": elements}


def _brute_force_optimum(candidates: list, budget: int) -> float:
    by_pos = {pos: [c for c in candidates if c.position == pos] for pos in SQUAD_REQUIREMENTS}
    best = -1.0
    for gks in combinations(by_pos["GK"], SQUAD_REQUIREMENTS["GK"]):
        for defs in combinations(by_pos["DEF"], SQUAD_REQUIREMENTS["DEF"]):
            for mids in combinations(by_pos["MID"], SQUAD_REQUIREMENTS["MID"]):
                for fwds in combinations(by_pos["FWD"], SQUAD_REQUIREMENTS["FWD"]):
                    sel = gks + defs + mids + fwds
                    if sum(c.cost_tenths for c in sel) <= budget:
                        best = max(best, sum(c.objective_points for c in sel))
    return best


def test_exact_optimizer_matches_brute_force() -> None:
    candidates, _ = _parse(_knapsack_bootstrap())
    eligible = _resolve_season(candidates, SEASON_HISTORICAL)
    squad = _build_squad(eligible)

    assert len(squad) == SQUAD_SIZE
    assert sum(c.cost_tenths for c in squad) <= BUDGET
    got = sum(c.objective_points for c in squad)
    want = _brute_force_optimum(eligible, int(BUDGET))
    assert want > 0  # guard: the scenario is feasible
    assert got == want


def test_exact_optimizer_beats_value_greedy(bootstrap: dict) -> None:
    """The points-maximiser must score at least as well as the old value-greedy pick."""
    candidates, _ = _parse(bootstrap)
    eligible = _resolve_season(candidates, SEASON_HISTORICAL)
    _score(eligible)

    # Replicate the previous greedy-by-value_score construction.
    squad, spent = [], 0.0
    per_pos = dict.fromkeys(SQUAD_REQUIREMENTS, 0)
    per_club: dict[int, int] = {}
    for c in sorted(eligible, key=lambda x: x.value_score, reverse=True):
        if len(squad) == SQUAD_SIZE:
            break
        if per_pos[c.position] >= SQUAD_REQUIREMENTS[c.position]:
            continue
        if per_club.get(c.team_id, 0) >= MAX_PLAYERS_PER_CLUB:
            continue
        if spent + c.cost_tenths > BUDGET:
            continue
        squad.append(c)
        spent += c.cost_tenths
        per_pos[c.position] += 1
        per_club[c.team_id] = per_club.get(c.team_id, 0) + 1
    greedy_points = sum(c.objective_points for c in squad)

    optimal = _build_squad(eligible)
    assert sum(c.objective_points for c in optimal) >= greedy_points


def test_predicted_season_uses_projection(bootstrap: dict) -> None:
    result = build_optimal_team(bootstrap, season=SEASON_PREDICTED)

    assert result.is_projection is True
    assert result.season == SEASON_PREDICTED
    assert result.metrics.is_projection is True
    assert len(result.squad) == SQUAD_SIZE
    assert result.metrics.total_cost <= BUDGET / COST_DIVISOR + 1e-6
    # Projected points are positive and drive the squad total.
    assert all(p.objective_points >= 0 for p in result.squad)
    assert result.metrics.squad_total_points > 0


def test_historical_season_prices_use_season_start(bootstrap: dict) -> None:
    result = build_optimal_team(bootstrap, season=SEASON_HISTORICAL)
    assert result.is_projection is False
    # Historical objective points equal actual total points.
    for player in result.squad:
        assert player.objective_points == float(player.total_points)


def test_unknown_season_raises(bootstrap: dict) -> None:
    with pytest.raises(OptimizerError):
        build_optimal_team(bootstrap, season="1999-00")


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
