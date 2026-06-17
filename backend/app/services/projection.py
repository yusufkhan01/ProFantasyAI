"""Forward-looking expected-points (xP) projection for the upcoming season.

The FPL API only ever publishes the *current* season, so we cannot know next
season's actual returns. Instead we project each player's points from the most
recently completed season using a small, transparent model:

1. Start from a per-90 scoring rate, blending the player's **actual** points-per-90
   with an **underlying** estimate built from expected goals/assists and an
   expected clean-sheet rate. Blending in the underlying numbers strips out some
   of the finishing luck that makes raw points a noisy predictor.
2. Regress that rate towards the position's minutes-weighted average. Players with
   few minutes get pulled harder towards the mean (classic shrinkage), so a
   100-minute hot streak can't masquerade as a season-long elite rate.
3. Multiply the regressed rate by projected minutes (last season's minutes, capped
   at a full campaign and given a small uncertainty haircut).

Every constant below is intentionally simple and easy to tune; the goal is an
honest, explainable baseline rather than a black box. When the real upcoming
season is published the same model can run on it directly.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from math import exp
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid a circular import with the optimizer at runtime
    from app.services.optimizer import Candidate

# FPL scoring points awarded per goal/assist/clean sheet, by position.
GOAL_POINTS: dict[str, int] = {"GK": 6, "DEF": 6, "MID": 5, "FWD": 4}
ASSIST_POINTS = 3
CLEAN_SHEET_POINTS: dict[str, int] = {"GK": 4, "DEF": 4, "MID": 1, "FWD": 0}
APPEARANCE_POINTS_PER_90 = 2.0  # a full 90 minutes earns 2 appearance points

# Model hyper-parameters (tunable).
BLEND_ACTUAL = 0.6  # weight on actual points-per-90 vs. underlying xG/xA estimate
PRIOR_MINUTES = 900.0  # strength of regression-to-mean (~10 full matches)
MAX_SEASON_MINUTES = 3420.0  # 38 matches * 90 minutes
MINUTES_RETENTION = 0.92  # haircut for next-season availability uncertainty


def _games90(minutes: float) -> float:
    return minutes / 90.0 if minutes > 0 else 0.0


def _underlying_p90(candidate: Candidate) -> float:
    """Expected points per 90 from underlying numbers (xG, xA, clean sheets)."""
    pos = candidate.position
    attacking = GOAL_POINTS.get(pos, 4) * candidate.xg90 + ASSIST_POINTS * candidate.xa90
    # Poisson P(0 goals conceded) = exp(-xGC/90); clean sheets only matter for GK/DEF/MID.
    clean_sheet = CLEAN_SHEET_POINTS.get(pos, 0) * exp(-candidate.xgc90)
    return APPEARANCE_POINTS_PER_90 + attacking + clean_sheet


def _position_mean_p90(candidates: Sequence[Candidate]) -> dict[str, float]:
    """Minutes-weighted mean points-per-90 for each position (the shrinkage prior)."""
    points: dict[str, float] = {}
    games: dict[str, float] = {}
    for c in candidates:
        g = _games90(c.minutes)
        if g <= 0:
            continue
        points[c.position] = points.get(c.position, 0.0) + c.total_points
        games[c.position] = games.get(c.position, 0.0) + g
    return {pos: (points[pos] / games[pos]) if games.get(pos) else 0.0 for pos in points}


def project_points(candidate: Candidate, position_mean_p90: dict[str, float]) -> float:
    """Projected total points for ``candidate`` over the upcoming season."""
    games = _games90(candidate.minutes)
    if games <= 0:
        return 0.0

    actual_p90 = candidate.total_points / games
    blended_p90 = BLEND_ACTUAL * actual_p90 + (1 - BLEND_ACTUAL) * _underlying_p90(candidate)

    # Shrink towards the position mean; low-minute players are pulled harder.
    mean_p90 = position_mean_p90.get(candidate.position, blended_p90)
    regressed_p90 = (candidate.minutes * blended_p90 + PRIOR_MINUTES * mean_p90) / (
        candidate.minutes + PRIOR_MINUTES
    )

    projected_minutes = min(candidate.minutes, MAX_SEASON_MINUTES) * MINUTES_RETENTION
    return round(regressed_p90 * projected_minutes / 90.0, 1)


def compute_projections(candidates: Iterable[Candidate]) -> None:
    """Set ``projected_points`` on every candidate (mutates in place)."""
    candidates = list(candidates)
    means = _position_mean_p90(candidates)
    for candidate in candidates:
        candidate.projected_points = project_points(candidate, means)
