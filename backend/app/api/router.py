"""API router aggregation (versioned business routes)."""

from fastapi import APIRouter

from app.routers import ai, charts, dashboard, forecasting, operations


def build_api_router() -> APIRouter:
    """Compose versioned API routes."""
    api = APIRouter()
    api.include_router(dashboard.router)
    api.include_router(charts.router)
    api.include_router(operations.router)
    api.include_router(forecasting.router)
    api.include_router(ai.router)
    return api
