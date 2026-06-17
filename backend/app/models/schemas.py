"""Pydantic models that define the public API response shapes."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Player(BaseModel):
    """A single FPL player enriched with the computed value score."""

    id: int
    name: str = Field(..., description="Short display name (web_name).")
    full_name: str
    position: str = Field(..., description="One of GK, DEF, MID, FWD.")
    team_id: int
    team: str
    team_short: str
    price: float = Field(..., description="Price in millions, e.g. 12.5.")
    total_points: int
    form: float
    points_per_game: float
    ict_index: float
    selected_by_percent: float
    value_score: float = Field(..., description="Normalised weighted value score (0-100).")
    is_captain: bool = False


class TeamMetrics(BaseModel):
    """Aggregate metrics describing the assembled squad."""

    formation: str = Field(..., description="Starting XI shape, e.g. 3-4-3.")
    total_cost: float = Field(..., description="Total squad cost in millions.")
    budget_remaining: float
    squad_total_points: int
    starting_total_points: int


class OptimalTeamResponse(BaseModel):
    """The full optimisation result returned by ``GET /api/optimal-team``."""

    starting_xi: list[Player]
    bench: list[Player]
    squad: list[Player]
    captain_id: int
    metrics: TeamMetrics
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
