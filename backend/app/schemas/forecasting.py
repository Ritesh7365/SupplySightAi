"""Forecast response schemas."""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from app.schemas.common import ORMModel


class ForecastPoint(ORMModel):
    period: str
    yhat: float
    yhat_lower: float
    yhat_upper: float
    is_forecast: bool = False


class ForecastResponse(ORMModel):
    metric: str
    model: str
    history: List[ForecastPoint] = Field(default_factory=list)
    forecast: List[ForecastPoint] = Field(default_factory=list)
    mape: Optional[float] = None
