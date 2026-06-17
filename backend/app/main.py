"""ProFantasyAI FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="ProFantasyAI API",
    description=(
        "Builds the optimal Fantasy Premier League squad from live FPL data using a "
        "normalised, weighted value model. Interactive docs available at /docs."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """Service banner with pointers to docs and health."""
    return {"name": settings.app_name, "docs": "/docs", "health": "/api/health"}
