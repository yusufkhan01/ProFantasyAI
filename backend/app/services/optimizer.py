"""FPL squad optimisation.

The pipeline is:

1. Parse the raw ``bootstrap-static`` payload into typed ``Candidate`` rows.
2. Resolve a *season*: this fixes each player's price and the per-player number we
   maximise (the "objective"):
   - ``2025-26`` (historical): real season-start price and **actual** total points.
   - ``2026-27`` (predicted): current price as a proxy and **projected** points.
3. Assemble the squad that **maximises total objective points** under the FPL
   budget, positional and max-per-club constraints. This is an exact knapsack
   (per-position dynamic programming + an optimal budget split), not a greedy
   heuristic, so it never leaves value on the table the way sorting-by-score does.
4. Pick the highest-scoring valid starting XI (and therefore the formation),
   captain, and bench.

A separate, normalised weighted *value model* still powers the "best value
players" leaderboard, where points-per-cost is genuinely what you want to rank by.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import product
from typing import Any

from app.core.constants import (
    BUDGET,
    COST_DIVISOR,
    DEFAULT_SEASON,
    FORMATION_BOUNDS,
    MAX_PLAYERS_PER_CLUB,
    POSITION_BY_ELEMENT_TYPE,
    SEASON_PREDICTED,
    SEASONS,
    SQUAD_REQUIREMENTS,
    SQUAD_SIZE,
    STARTING_XI_SIZE,
)
from app.models.schemas import OptimalTeamResponse, Player, TeamMetrics
from app.services.projection import compute_projections

# Weights for the value model. They must sum to 1.0.
VALUE_WEIGHTS: dict[str, float] = {
    "points_per_cost": 0.45,
    "form": 0.25,
    "points_per_game": 0.20,
    "ict_index": 0.10,
}

_NEG = -1e18  # sentinel for "infeasible" inside the knapsack tables


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
    now_cost: int  # current price in FPL tenths-of-a-million units
    start_cost: int  # season-start price in the same units
    total_points: int
    form: float
    points_per_game: float
    ict_index: float
    selected_by_percent: float
    minutes: int
    status: str
    # underlying numbers used by the projection model
    xg90: float
    xa90: float
    xgc90: float
    # derived
    points_per_cost: float = 0.0
    value_score: float = 0.0
    projected_points: float = 0.0
    # resolved per season at build time
    cost_tenths: int = 0
    objective_points: float = 0.0


def _to_float(value: Any) -> float:
    """Coerce FPL fields (often strings) to float, defaulting to 0.0."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    """Coerce FPL fields to int, defaulting to 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _parse(bootstrap: dict[str, Any]) -> tuple[list[Candidate], dict[int, dict[str, Any]]]:
    teams: dict[int, dict[str, Any]] = {
        team["id"]: {
            "name": team.get("name", "Unknown"),
            "short": team.get("short_name", ""),
            # Stable club code (distinct from the season id) used for crest images.
            "code": _to_int(team.get("code")),
        }
        for team in bootstrap.get("teams", [])
    }

    candidates: list[Candidate] = []
    for element in bootstrap.get("elements", []):
        position = POSITION_BY_ELEMENT_TYPE.get(element.get("element_type"))
        if position is None:
            continue
        now_cost = _to_int(element.get("now_cost"))
        if now_cost <= 0:
            continue
        # cost_change_start is the change since the season opened, so subtract it
        # to recover the price you would actually have paid at GW1.
        start_cost = now_cost - _to_int(element.get("cost_change_start"))
        start_cost = max(start_cost, 1)
        total_points = _to_int(element.get("total_points"))
        first = str(element.get("first_name", "")).strip()
        last = str(element.get("second_name", "")).strip()
        candidates.append(
            Candidate(
                id=int(element["id"]),
                name=element.get("web_name", ""),
                full_name=f"{first} {last}".strip(),
                position=position,
                team_id=int(element.get("team", 0)),
                now_cost=now_cost,
                start_cost=start_cost,
                total_points=total_points,
                form=_to_float(element.get("form")),
                points_per_game=_to_float(element.get("points_per_game")),
                ict_index=_to_float(element.get("ict_index")),
                selected_by_percent=_to_float(element.get("selected_by_percent")),
                minutes=_to_int(element.get("minutes")),
                status=str(element.get("status", "a")),
                xg90=_to_float(element.get("expected_goals_per_90")),
                xa90=_to_float(element.get("expected_assists_per_90")),
                xgc90=_to_float(element.get("expected_goals_conceded_per_90")),
                points_per_cost=(total_points / (now_cost / COST_DIVISOR)) if now_cost else 0.0,
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


# --------------------------------------------------------------------------- #
# Exact squad optimisation (maximise total objective points under constraints)
# --------------------------------------------------------------------------- #
def _position_curve(players: Sequence[Candidate], k: int, budget: int) -> list[float]:
    """Best objective for choosing *exactly* ``k`` players costing at most ``b``.

    Returns a list indexed by budget ``b`` in 0..``budget`` (monotonic in ``b``).
    """
    dp = [[_NEG] * (budget + 1) for _ in range(k + 1)]
    dp[0] = [0.0] * (budget + 1)
    for c in players:
        cost, val = c.cost_tenths, c.objective_points
        if cost > budget:
            continue
        for j in range(k, 0, -1):
            row, prev = dp[j], dp[j - 1]
            for b in range(budget, cost - 1, -1):
                cand = prev[b - cost] + val
                if cand > row[b]:
                    row[b] = cand
    best = dp[k]
    for b in range(1, budget + 1):  # make monotonic: best with cost <= b
        if best[b - 1] > best[b]:
            best[b] = best[b - 1]
    return best


def _convolve(f: list[float], g: list[float]) -> tuple[list[float], list[int]]:
    """Combine two budget curves: out[b] = max_{i<=b} f[i] + g[b-i].

    ``split[b]`` records the budget ``i`` handed to ``f`` at the optimum.
    """
    n = len(f)
    out = [_NEG] * n
    split = [0] * n
    for i in range(n):
        if f[i] <= _NEG:
            continue
        fi = f[i]
        for b in range(i, n):
            cand = fi + g[b - i]
            if cand > out[b]:
                out[b] = cand
                split[b] = i
    return out, split


def _reconstruct_position(players: Sequence[Candidate], k: int, budget: int) -> list[Candidate]:
    """Recover the actual ``k`` players that achieve the position optimum at ``budget``."""
    n = len(players)
    if k == 0 or n == 0:
        return []
    dp = [[_NEG] * (budget + 1) for _ in range(k + 1)]
    dp[0] = [0.0] * (budget + 1)
    take = [[[False] * (budget + 1) for _ in range(k + 1)] for _ in range(n)]
    for idx, c in enumerate(players):
        cost, val = c.cost_tenths, c.objective_points
        if cost > budget:
            continue
        for j in range(k, 0, -1):
            row, prev, tk = dp[j], dp[j - 1], take[idx][j]
            for b in range(budget, cost - 1, -1):
                cand = prev[b - cost] + val
                if cand > row[b]:
                    row[b] = cand
                    tk[b] = True
    best_b = max(range(budget + 1), key=lambda b: dp[k][b])
    chosen: list[Candidate] = []
    j, b = k, best_b
    for idx in range(n - 1, -1, -1):
        if j == 0:
            break
        if take[idx][j][b]:
            c = players[idx]
            chosen.append(c)
            b -= c.cost_tenths
            j -= 1
    return chosen


def _club_counts(squad: Sequence[Candidate]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for c in squad:
        counts[c.team_id] = counts.get(c.team_id, 0) + 1
    return counts


def _exact_squad(candidates: Sequence[Candidate], budget: int) -> list[Candidate]:
    """Exact max-objective squad ignoring the per-club cap (handled by repair)."""
    by_pos = {pos: [c for c in candidates if c.position == pos] for pos in SQUAD_REQUIREMENTS}
    for pos, need in SQUAD_REQUIREMENTS.items():
        if len(by_pos[pos]) < need:
            return []

    order = ["GK", "DEF", "MID", "FWD"]
    curves = {pos: _position_curve(by_pos[pos], SQUAD_REQUIREMENTS[pos], budget) for pos in order}

    combined = curves["GK"]
    splits: list[tuple[str, list[int]]] = []
    for pos in order[1:]:
        combined, split = _convolve(combined, curves[pos])
        splits.append((pos, split))

    if combined[budget] <= _NEG:
        return []

    # Backtrack the chain ((GK*DEF)*MID)*FWD to recover each position's budget.
    # Each split records the budget handed to the left-hand block, so peeling from
    # the outside (FWD, then MID, then DEF) leaves GK's budget in `remaining`.
    pos_budget: dict[str, int] = {}
    remaining = budget
    for pos, split in reversed(splits):  # FWD, then MID, then DEF
        block = split[remaining]  # budget kept by everything left of `pos`
        pos_budget[pos] = remaining - block
        remaining = block
    pos_budget["GK"] = remaining

    squad: list[Candidate] = []
    for pos in order:
        squad += _reconstruct_position(by_pos[pos], SQUAD_REQUIREMENTS[pos], pos_budget[pos])
    return squad if len(squad) == SQUAD_SIZE else []


def _repair_clubs(squad: list[Candidate], pool: Sequence[Candidate]) -> list[Candidate]:
    """Restore the max-per-club rule by swapping out the weakest offenders.

    Only runs in the rare case where the exact (club-relaxed) optimum exceeds the
    per-club cap; a constraint-preserving local search afterwards recovers quality.
    """
    squad = squad[:]
    for _ in range(SQUAD_SIZE * MAX_PLAYERS_PER_CLUB):
        counts = _club_counts(squad)
        over = [team for team, n in counts.items() if n > MAX_PLAYERS_PER_CLUB]
        if not over:
            break
        team = over[0]
        out_c = min((c for c in squad if c.team_id == team), key=lambda c: c.objective_points)
        ids = {c.id for c in squad}
        budget_left = BUDGET - (sum(c.cost_tenths for c in squad) - out_c.cost_tenths)
        swaps = [
            c
            for c in pool
            if c.id not in ids
            and c.position == out_c.position
            and counts.get(c.team_id, 0) < MAX_PLAYERS_PER_CLUB
        ]
        affordable = [c for c in swaps if c.cost_tenths <= budget_left]
        if affordable:  # best replacement we can afford
            replacement = max(affordable, key=lambda c: c.objective_points)
        elif swaps:  # nothing affordable: free up cash with the cheapest swap
            replacement = min(swaps, key=lambda c: c.cost_tenths)
        else:
            break
        squad[squad.index(out_c)] = replacement
    return squad


def _local_search(squad: list[Candidate], pool: Sequence[Candidate]) -> list[Candidate]:
    """Constraint-preserving objective-improving 1-swaps from a feasible squad."""
    squad = squad[:]
    improved = True
    while improved:
        improved = False
        ids = {c.id for c in squad}
        spent = sum(c.cost_tenths for c in squad)
        counts = _club_counts(squad)
        for i, out_c in enumerate(squad):
            best_gain, best_in = 0.0, None
            for cand in pool:
                if cand.id in ids or cand.position != out_c.position:
                    continue
                gain = cand.objective_points - out_c.objective_points
                if gain <= best_gain:
                    continue
                if spent - out_c.cost_tenths + cand.cost_tenths > BUDGET:
                    continue
                if (
                    cand.team_id != out_c.team_id
                    and counts.get(cand.team_id, 0) >= MAX_PLAYERS_PER_CLUB
                ):
                    continue
                best_gain, best_in = gain, cand
            if best_in is not None:
                squad[i] = best_in
                improved = True
                break
    return squad


def _build_squad(candidates: list[Candidate]) -> list[Candidate]:
    """Assemble the max-objective 15-man squad respecting every FPL constraint."""
    squad = _exact_squad(candidates, int(BUDGET))
    if not squad:
        return []
    counts = _club_counts(squad)
    if counts and max(counts.values()) > MAX_PLAYERS_PER_CLUB:
        # Rare: the unconstrained optimum stacks one club, so repair then polish.
        squad = _local_search(_repair_clubs(squad, candidates), candidates)
    return squad


def _pick_starting_xi(
    squad: list[Candidate], key: Callable[[Candidate], float]
) -> tuple[list[Candidate], list[Candidate], str]:
    """Choose the highest-scoring valid starting XI and resulting formation."""
    by_position = {
        position: sorted((c for c in squad if c.position == position), key=key, reverse=True)
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
        total = sum(key(c) for c in selection)
        if best is None or total > best[0]:
            best = (total, (defenders, midfielders, forwards), selection)

    if best is None:
        raise OptimizerError("Could not assemble a valid starting XI from the squad.")

    _, (defenders, midfielders, forwards), starting = best
    starting_ids = {c.id for c in starting}
    bench = sorted((c for c in squad if c.id not in starting_ids), key=key, reverse=True)
    formation = f"{defenders}-{midfielders}-{forwards}"
    return starting, bench, formation


def _to_player(
    candidate: Candidate, teams: dict[int, dict[str, Any]], *, is_captain: bool = False
) -> Player:
    team = teams.get(candidate.team_id, {"name": "Unknown", "short": "UNK", "code": 0})
    return Player(
        id=candidate.id,
        name=candidate.name,
        full_name=candidate.full_name or candidate.name,
        position=candidate.position,
        team_id=candidate.team_id,
        team=team["name"],
        team_short=team["short"],
        team_code=int(team.get("code", 0)),
        price=round(candidate.cost_tenths / COST_DIVISOR, 1),
        total_points=candidate.total_points,
        form=candidate.form,
        points_per_game=candidate.points_per_game,
        ict_index=candidate.ict_index,
        selected_by_percent=candidate.selected_by_percent,
        value_score=candidate.value_score,
        objective_points=round(candidate.objective_points, 1),
        is_captain=is_captain,
    )


def _resolve_season(candidates: list[Candidate], season: str) -> list[Candidate]:
    """Set each candidate's price (``cost_tenths``) and ``objective_points`` for ``season``.

    Returns the eligible pool for that season.
    """
    if season == SEASON_PREDICTED:
        compute_projections(candidates)
        for c in candidates:
            c.cost_tenths = c.now_cost
            c.objective_points = c.projected_points
        # Project only players who actually featured and are currently available.
        eligible = [c for c in candidates if c.status == "a" and c.minutes > 0]
    else:  # historical: the season you could have built at GW1
        for c in candidates:
            c.cost_tenths = c.start_cost
            c.objective_points = float(c.total_points)
        eligible = [c for c in candidates if c.minutes > 0]

    if len(eligible) < SQUAD_SIZE:  # pre-season / sparse data safety net
        eligible = candidates
    return eligible


def build_optimal_team(
    bootstrap: dict[str, Any], season: str = DEFAULT_SEASON
) -> OptimalTeamResponse:
    """Build the optimal squad, starting XI, formation and captain for ``season``."""
    if season not in SEASONS:
        raise OptimizerError(f"Unknown season '{season}'. Expected one of {SEASONS}.")

    candidates, teams = _parse(bootstrap)
    _score(candidates)  # value model (leaderboard) is independent of the season
    eligible = _resolve_season(candidates, season)

    squad = _build_squad(eligible)
    if len(squad) < SQUAD_SIZE:
        raise OptimizerError(
            "Could not build a full 15-player squad within the budget and constraints."
        )

    starting, bench, formation = _pick_starting_xi(squad, key=lambda c: c.objective_points)
    captain = max(starting, key=lambda c: c.objective_points)
    is_projection = season == SEASON_PREDICTED

    total_cost = round(sum(c.cost_tenths for c in squad) / COST_DIVISOR, 1)
    metrics = TeamMetrics(
        season=season,
        is_projection=is_projection,
        formation=formation,
        total_cost=total_cost,
        budget_remaining=round(BUDGET / COST_DIVISOR - total_cost, 1),
        squad_total_points=round(sum(c.objective_points for c in squad), 1),
        starting_total_points=round(sum(c.objective_points for c in starting), 1),
    )

    return OptimalTeamResponse(
        season=season,
        is_projection=is_projection,
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
    candidates, teams = _parse(bootstrap)
    eligible = [c for c in candidates if c.status == "a" and c.minutes > 0]
    if len(eligible) < SQUAD_SIZE:
        eligible = candidates
    _score(eligible)
    for c in eligible:  # leaderboard shows current price + actual points
        c.cost_tenths = c.now_cost
        c.objective_points = float(c.total_points)
    pool = [c for c in eligible if position is None or c.position == position]
    pool.sort(key=lambda c: c.value_score, reverse=True)
    return [_to_player(c, teams) for c in pool[:limit]]
