"""Revenue / demand forecasting over analytics.mv_monthly_sales."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseError, NotFoundError
from app.core.logging import get_logger
from app.models.analytics_views import MonthlySalesMatView
from app.schemas.forecasting import ForecastPoint, ForecastResponse

logger = get_logger("services.forecasting")


def _parse_period(year_month: str) -> Tuple[int, int]:
    year_s, month_s = year_month.split("-")
    return int(year_s), int(month_s)


def _next_periods(last: str, n: int) -> List[str]:
    year, month = _parse_period(last)
    out: List[str] = []
    for _ in range(n):
        month += 1
        if month > 12:
            month = 1
            year += 1
        out.append(f"{year:04d}-{month:02d}")
    return out


def _linear_forecast(
    history: List[Tuple[str, float]],
    periods: int,
) -> Tuple[List[ForecastPoint], List[ForecastPoint], str, Optional[float]]:
    """Simple least-squares trend with residual-based confidence band."""
    n = len(history)
    xs = list(range(n))
    ys = [v for _, v in history]
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    denom = sum((x - x_mean) ** 2 for x in xs) or 1.0
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    intercept = y_mean - slope * x_mean

    fitted = [intercept + slope * x for x in xs]
    residuals = [y - f for y, f in zip(ys, fitted)]
    sigma = (sum(r * r for r in residuals) / max(n - 2, 1)) ** 0.5
    band = max(sigma * 1.96, y_mean * 0.05)

    hist_points = [
        ForecastPoint(
            period=period,
            yhat=round(fit, 2),
            yhat_lower=round(max(fit - band, 0), 2),
            yhat_upper=round(fit + band, 2),
            is_forecast=False,
        )
        for (period, _), fit in zip(history, fitted)
    ]

    # MAPE on history
    mape_vals = []
    for y, f in zip(ys, fitted):
        if abs(y) > 1e-9:
            mape_vals.append(abs((y - f) / y) * 100)
    mape = round(sum(mape_vals) / len(mape_vals), 2) if mape_vals else None

    last_period = history[-1][0]
    future_periods = _next_periods(last_period, periods)
    forecast_points: List[ForecastPoint] = []
    for i, period in enumerate(future_periods, start=1):
        yhat = intercept + slope * (n - 1 + i)
        widen = band * (1 + 0.08 * i)
        forecast_points.append(
            ForecastPoint(
                period=period,
                yhat=round(max(yhat, 0), 2),
                yhat_lower=round(max(yhat - widen, 0), 2),
                yhat_upper=round(max(yhat + widen, 0), 2),
                is_forecast=True,
            )
        )

    return hist_points, forecast_points, "linear_trend", mape


def _prophet_forecast(
    history: List[Tuple[str, float]],
    periods: int,
) -> Optional[Tuple[List[ForecastPoint], List[ForecastPoint], str, Optional[float]]]:
    try:
        import pandas as pd
        from prophet import Prophet
    except Exception:  # noqa: BLE001
        return None

    try:
        df = pd.DataFrame(
            {
                "ds": [datetime.strptime(p + "-01", "%Y-%m-%d") for p, _ in history],
                "y": [v for _, v in history],
            }
        )
        model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        model.fit(df)
        future = model.make_future_dataframe(periods=periods, freq="MS")
        forecast = model.predict(future)

        hist_n = len(history)
        hist_points = [
            ForecastPoint(
                period=history[i][0],
                yhat=round(float(forecast.loc[i, "yhat"]), 2),
                yhat_lower=round(float(forecast.loc[i, "yhat_lower"]), 2),
                yhat_upper=round(float(forecast.loc[i, "yhat_upper"]), 2),
                is_forecast=False,
            )
            for i in range(hist_n)
        ]
        forecast_points = [
            ForecastPoint(
                period=row["ds"].strftime("%Y-%m"),
                yhat=round(float(row["yhat"]), 2),
                yhat_lower=round(max(float(row["yhat_lower"]), 0), 2),
                yhat_upper=round(max(float(row["yhat_upper"]), 0), 2),
                is_forecast=True,
            )
            for _, row in forecast.iloc[hist_n:].iterrows()
        ]

        mape_vals = []
        for i, (_, y) in enumerate(history):
            f = float(forecast.loc[i, "yhat"])
            if abs(y) > 1e-9:
                mape_vals.append(abs((y - f) / y) * 100)
        mape = round(sum(mape_vals) / len(mape_vals), 2) if mape_vals else None
        return hist_points, forecast_points, "prophet", mape
    except Exception:  # noqa: BLE001
        logger.warning("Prophet forecast failed; falling back to linear trend", exc_info=True)
        return None


class ForecastingService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def revenue_forecast(self, *, periods: int = 6) -> ForecastResponse:
        try:
            rows = list(
                self.db.execute(
                    select(MonthlySalesMatView).order_by(
                        MonthlySalesMatView.year_number,
                        MonthlySalesMatView.month_number,
                    )
                )
                .scalars()
                .all()
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load monthly sales for forecast")
            raise DatabaseError("Unable to load forecast source data") from exc

        if len(rows) < 3:
            raise NotFoundError("Need at least 3 months of sales history to forecast")

        history = [(r.year_month, float(r.sales)) for r in rows]
        prophet = _prophet_forecast(history, periods)
        if prophet:
            hist_points, forecast_points, model, mape = prophet
        else:
            hist_points, forecast_points, model, mape = _linear_forecast(history, periods)

        return ForecastResponse(
            metric="revenue",
            model=model,
            history=hist_points,
            forecast=forecast_points,
            mape=mape,
        )
