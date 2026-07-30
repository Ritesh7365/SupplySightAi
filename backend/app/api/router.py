"""API router aggregation (versioned business routes)."""

from fastapi import APIRouter

from app.routers import charts, dashboard


def build_api_router() -> APIRouter:
    """Compose versioned API routes (dashboard + charts)."""
    api = APIRouter()
    api.include_router(dashboard.router)
    api.include_router(charts.router)
    return api
