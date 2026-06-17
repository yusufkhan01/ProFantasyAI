"""FPL squad optimisation.

The pipeline is:

1. Parse the raw ``bootstrap-static`` payload into typed ``Candidate`` rows.
2. Filter to players who are actually available and have played minutes.
3. Score every player with a *normalised* weighted value model so the weights
   are meaningful across metrics measured on different scales.
4. Greedily assemble a 15-man squad that respects the FPL budget, positional
   and max-per-club constraints.
5. Pick the highest-value valid starting XI (and therefore the formation),
   captain, and bench.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

from app.core.constants import (
    BUDGET,
    COST_DIVISOR,
    FORMATION_BOUNDS,
    MAX_PLAYERS_PER_CLUB,
    POSITION_BY_ELEMENT_TYPE,
    SQUAD_REQUIREMENTS,
    SQUAD_SIZE,
    STARTING_XI_SIZE,
)
from app.models.schemas import OptimalTeamResponse, Player, TeamMetrics

# Weights for the value model. They must sum to 1.0.
VALUE_WEIGHTS: dict[str, float] = {
    "points_per_cost": 0.45,
    "form": 0.25,
    "points_per_game": 0.20,
    "ict_index": 0.10,
}


class OptimizerError(RuntimeError):
    """Raised when a valid squad cannot be assembled from the supplied data."""


@dataclass
class Candidate:
    """A flattened, type-coerced view of an FPL player used during optimisation."""

    id: int
    name: str
    full_name: str
    position: str
    team_id: int
    price: float  # millions
    now_cost: float  # FPL tenths-of-a-million units
    total_points: int
    form: float
    points_per_game: float
    ict_index: float
    selected_by_percent: float
    minutes: int
    status: str
    points_per_cost: float = 0.0
    value_score: float = 0.0


def _to_float(value: Any) -> float:
    """Coerce FPL fields (often strings) to float, defaulting to 0.0."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _is_eligible(candidate: Candidate) -> bool:
    """Only consider players who are available and have actually played."""
    return candidate.status == "a" and candidate.minutes > 0


def _parse(bootstrap: dict[str, Any]) -> tuple[list[Candidate], dict[int, dict[str, str]]]:
    teams = {
        team["id"]: {"name": team.get("name", "Unknown"), "short": team.get("short_name", "")}
        for team in bootstrap.get("teams", [])
    }

    candidates: list[Candidate] = []
    for element in bootstrap.get("elements", []):
        position = POSITION_BY_ELEMENT_TYPE.get(element.get("element_type"))
        if position is None:
            continue
        now_cost = _to_float(element.get("now_cost"))
        if now_cost <= 0:
            continue
        price = now_cost / COST_DIVISOR
        total_points = int(element.get("total_points", 0) or 0)
        first = str(element.get("first_name", "")).strip()
        last = str(element.get("second_name", "")).strip()
        candidates.append(
            Candidate(
                id=int(element["id"]),
                name=element.get("web_name", ""),
                full_name=f"{first} {last}".strip(),
                position=position,
                team_id=int(element.get("team", 0)),
                price=price,
                now_cost=now_cost,
                total_points=total_points,
                form=_to_float(element.get("form")),
                points_per_game=_to_float(element.get("points_per_game")),
                ict_index=_to_float(element.get("ict_index")),
                selected_by_percent=_to_float(element.get("selected_by_percent")),
                minutes=int(element.get("minutes", 0) or 0),
                status=str(element.get("status", "a")),
                points_per_cost=(total_points / price) if price else 0.0,
            )
        )
    return candidates, teams


def _normalise(values: list[float]) -> list[float]:
    """Min-max scale a list of values into the 0..1 range."""
    low, high = min(values), max(values)
    span = high - low
    if span == 0:
        return [0.0 for _ in values]
    return [(value - low) / span for value in values]


def _score(candidates: list[Candidate]) -> None:
    """Assign each candidate a 0-100 value score (mutates in place)."""
    if not candidates:
        return
    normalised = {
        "points_per_cost": _normalise([c.points_per_cost for c in candidates]),
        "form": _normalise([c.form for c in candidates]),
        "points_per_game": _normalise([c.points_per_game for c in candidates]),
        "ict_index": _normalise([c.ict_index for c in candidates]),
    }
    for index, candidate in enumerate(candidates):
        score = sum(weight * normalised[metric][index] for metric, weight in VALUE_WEIGHTS.items())
        candidate.value_score = round(score * 100, 2)


def _build_squad(candidates: list[Candidate]) -> list[Candidate]:
    """Greedily pick the highest-value squad satisfying all FPL constraints."""
    ordered = sorted(candidates, key=lambda c: c.value_score, reverse=True)
    squad: list[Candidate] = []
    spent = 0.0
    per_position = dict.fromkeys(SQUAD_REQUIREMENTS, 0)
    per_club: dict[int, int] = {}

    for candidate in ordered:
        if len(squad) == SQUAD_SIZE:
            break
        if per_position[candidate.position] >= SQUAD_REQUIREMENTS[candidate.position]:
            continue
        if per_club.get(candidate.team_id, 0) >= MAX_PLAYERS_PER_CLUB:
            continue
        if spent + candidate.now_cost > BUDGET:
            continue
        squad.append(candidate)
        spent += candidate.now_cost
        per_position[candidate.position] += 1
        per_club[candidate.team_id] = per_club.get(candidate.team_id, 0) + 1

    return squad


def _pick_starting_xi(squad: list[Candidate]) -> tuple[list[Candidate], list[Candidate], str]:
    """Choose the highest-value valid starting XI and resulting formation."""
    by_position = {
        position: sorted(
            (c for c in squad if c.position == position),
            key=lambda c: c.value_score,
            reverse=True,
        )
        for position in SQUAD_REQUIREMENTS
    }

    def_lo, def_hi = FORMATION_BOUNDS["DEF"]
    mid_lo, mid_hi = FORMATION_BOUNDS["MID"]
    fwd_lo, fwd_hi = FORMATION_BOUNDS["FWD"]

    best: tuple[float, tuple[int, int, int], list[Candidate]] | None = None
    for defenders, midfielders, forwards in product(
        range(def_lo, def_hi + 1),
        range(mid_lo, mid_hi + 1),
        range(fwd_lo, fwd_hi + 1),
    ):
        if 1 + defenders + midfielders + forwards != STARTING_XI_SIZE:
            continue
        if (
            len(by_position["GK"]) < 1
            or len(by_position["DEF"]) < defenders
            or len(by_position["MID"]) < midfielders
            or len(by_position["FWD"]) < forwards
        ):
            continue
        selection = (
            by_position["GK"][:1]
            + by_position["DEF"][:defenders]
            + by_position["MID"][:midfielders]
            + by_position["FWD"][:forwards]
        )
        total_value = sum(c.value_score for c in selection)
        if best is None or total_value > best[0]:
            best = (total_value, (defenders, midfielders, forwards), selection)

    if best is None:
        raise OptimizerError("Could not assemble a valid starting XI from the squad.")

    _, (defenders, midfielders, forwards), starting = best
    starting_ids = {c.id for c in starting}
    bench = sorted(
        (c for c in squad if c.id not in starting_ids),
        key=lambda c: c.value_score,
        reverse=True,
    )
    formation = f"{defenders}-{midfielders}-{forwards}"
    return starting, bench, formation


def _to_player(
    candidate: Candidate, teams: dict[int, dict[str, str]], *, is_captain: bool = False
) -> Player:
    team = teams.get(candidate.team_id, {"name": "Unknown", "short": "UNK"})
    return Player(
        id=candidate.id,
        name=candidate.name,
        full_name=candidate.full_name or candidate.name,
        position=candidate.position,
        team_id=candidate.team_id,
        team=team["name"],
        team_short=team["short"],
        price=round(candidate.price, 1),
        total_points=candidate.total_points,
        form=candidate.form,
        points_per_game=candidate.points_per_game,
        ict_index=candidate.ict_index,
        selected_by_percent=candidate.selected_by_percent,
        value_score=candidate.value_score,
        is_captain=is_captain,
    )


def _eligible_scored(
    bootstrap: dict[str, Any],
) -> tuple[list[Candidate], dict[int, dict[str, str]]]:
    candidates, teams = _parse(bootstrap)
    eligible = [c for c in candidates if _is_eligible(c)]
    # If the availability filter is too aggressive (e.g. pre-season), fall back.
    if len(eligible) < SQUAD_SIZE:
        eligible = candidates
    _score(eligible)
    return eligible, teams


def build_optimal_team(bootstrap: dict[str, Any]) -> OptimalTeamResponse:
    """Build the optimal squad, starting XI, formation and captain."""
    eligible, teams = _eligible_scored(bootstrap)

    squad = _build_squad(eligible)
    if len(squad) < SQUAD_SIZE:
        raise OptimizerError(
            "Could not build a full 15-player squad within the budget and constraints."
        )

    starting, bench, formation = _pick_starting_xi(squad)
    captain = max(starting, key=lambda c: c.value_score)

    total_cost = round(sum(c.price for c in squad), 1)
    metrics = TeamMetrics(
        formation=formation,
        total_cost=total_cost,
        budget_remaining=round(BUDGET / COST_DIVISOR - total_cost, 1),
        squad_total_points=sum(c.total_points for c in squad),
        starting_total_points=sum(c.total_points for c in starting),
    )

    return OptimalTeamResponse(
        starting_xi=[_to_player(c, teams, is_captain=c.id == captain.id) for c in starting],
        bench=[_to_player(c, teams) for c in bench],
        squad=[_to_player(c, teams, is_captain=c.id == captain.id) for c in squad],
        captain_id=captain.id,
        metrics=metrics,
    )


def value_leaders(
    bootstrap: dict[str, Any], *, limit: int = 20, position: str | None = None
) -> list[Player]:
    """Return the top players ranked by value score, optionally by position."""
    eligible, teams = _eligible_scored(bootstrap)
    pool = [c for c in eligible if position is None or c.position == position]
    pool.sort(key=lambda c: c.value_score, reverse=True)
    return [_to_player(c, teams) for c in pool[:limit]]
