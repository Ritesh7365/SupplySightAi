"""API router aggregation."""

from fastapi import APIRouter

from app.routers import charts, dashboard, health


def build_api_router() -> APIRouter:
    """Compose versioned API routes (dashboard + charts + health)."""
    api = APIRouter()
    api.include_router(health.router)
    api.include_router(dashboard.router)
    api.include_router(charts.router)
    return api
