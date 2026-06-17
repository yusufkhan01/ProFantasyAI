"""HTTP API routes for ProFantasyAI."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import Settings, get_settings
from app.models.schemas import HealthResponse, OptimalTeamResponse, Player
from app.services.fpl_client import FPLClient, FPLClientError, get_fpl_client
from app.services.optimizer import OptimizerError, build_optimal_team, value_leaders

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["meta"])
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Lightweight liveness probe."""
    return HealthResponse(app=settings.app_name)


@router.get("/optimal-team", response_model=OptimalTeamResponse, tags=["squad"])
async def optimal_team(client: FPLClient = Depends(get_fpl_client)) -> OptimalTeamResponse:
    """Build and return the optimal squad, starting XI, formation and captain."""
    try:
        bootstrap = await client.get_bootstrap()
        return build_optimal_team(bootstrap)
    except FPLClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except OptimizerError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.get("/players", response_model=list[Player], tags=["players"])
async def players(
    client: FPLClient = Depends(get_fpl_client),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of players to return."),
    position: str | None = Query(
        None, pattern="^(GK|DEF|MID|FWD)$", description="Optional position filter."
    ),
) -> list[Player]:
    """Return the best value-for-money players, ranked by value score."""
    try:
        bootstrap = await client.get_bootstrap()
        return value_leaders(bootstrap, limit=limit, position=position)
    except FPLClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
