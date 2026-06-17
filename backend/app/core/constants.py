"""Domain constants for Fantasy Premier League squad construction.

These encode the official FPL rules so the optimiser logic stays readable.
"""

from __future__ import annotations

# In the FPL API, ``now_cost`` is expressed in tenths of a million
# (e.g. 130 -> £13.0m), so we divide by this to get a price in millions.
COST_DIVISOR = 10.0

# Total squad budget in FPL "now_cost" units (1000 -> £100.0m).
BUDGET = 1000.0

# Squad composition required by the FPL rules.
SQUAD_REQUIREMENTS: dict[str, int] = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
SQUAD_SIZE = sum(SQUAD_REQUIREMENTS.values())  # 15

# Maximum number of players allowed from a single club.
MAX_PLAYERS_PER_CLUB = 3

# Map the FPL ``element_type`` ids to human-readable position codes.
POSITION_BY_ELEMENT_TYPE: dict[int, str] = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

# Valid starting-XI formation bounds (a goalkeeper is always required).
FORMATION_BOUNDS: dict[str, tuple[int, int]] = {
    "GK": (1, 1),
    "DEF": (3, 5),
    "MID": (2, 5),
    "FWD": (1, 3),
}
STARTING_XI_SIZE = 11

# Seasons the optimiser can build a squad for.
#
# ``bootstrap-static`` always serves the *latest* season. While 2025/26 is the
# most-recently-completed season it is the live payload, so ``SEASON_HISTORICAL``
# is built from real results. ``SEASON_PREDICTED`` is the upcoming season, which
# the FPL API does not publish until pre-season; until then we project it from the
# latest completed season's underlying numbers.
SEASON_HISTORICAL = "2025-26"
SEASON_PREDICTED = "2026-27"
DEFAULT_SEASON = SEASON_HISTORICAL
SEASONS: tuple[str, ...] = (SEASON_HISTORICAL, SEASON_PREDICTED)
