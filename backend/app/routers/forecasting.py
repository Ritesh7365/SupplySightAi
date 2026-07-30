"""Forecasting API router."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.deps import DbSession, OptionalUser
from app.schemas.common import OPENAPI_ERROR_RESPONSES
from app.schemas.forecasting import ForecastResponse
from app.services.forecasting_service import ForecastingService

router = APIRouter(
    prefix="/forecasting",
    tags=["Forecasting"],
    responses=OPENAPI_ERROR_RESPONSES,
)


@router.get(
    "/revenue",
    response_model=ForecastResponse,
    summary="Revenue forecast",
    description="Prophet when available; otherwise linear trend with confidence bands.",
)
def revenue_forecast(
    db: DbSession,
    _user: OptionalUser,
    periods: int = Query(default=6, ge=1, le=24),
) -> ForecastResponse:
    return ForecastingService(db).revenue_forecast(periods=periods)
