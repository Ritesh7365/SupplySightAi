"""Chart REST routers — series data for frontend visualizations."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from backend.app.core.deps import DbSession, OptionalUser
from backend.app.schemas.charts import (
    MonthlySalesChartResponse,
    TopCustomersChartResponse,
    TopProductsChartResponse,
)
from backend.app.services.chart_service import ChartService

router = APIRouter(prefix="/charts", tags=["Charts"])


@router.get(
    "/monthly-sales",
    response_model=MonthlySalesChartResponse,
    summary="Monthly sales time series",
    description=(
        "Monthly sales/profit/order series from ``analytics.mv_monthly_sales`` "
        "(materialized analytics view)."
    ),
)
def get_monthly_sales_chart(
    db: DbSession,
    _user: OptionalUser,
    year: Optional[int] = Query(default=None, ge=2000, le=2100),
) -> MonthlySalesChartResponse:
    return ChartService(db).monthly_sales(year=year)


@router.get(
    "/top-products",
    response_model=TopProductsChartResponse,
    summary="Top products by sales",
    description="Top N products from ``analytics.vw_product_performance`` ordered by best_selling_rank.",
)
def get_top_products_chart(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=10, ge=1, le=100),
) -> TopProductsChartResponse:
    return ChartService(db).top_products(limit=limit)


@router.get(
    "/top-customers",
    response_model=TopCustomersChartResponse,
    summary="Top customers by revenue",
    description="Top N customers from ``analytics.vw_customer_performance`` ordered by revenue_rank.",
)
def get_top_customers_chart(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=10, ge=1, le=100),
) -> TopCustomersChartResponse:
    return ChartService(db).top_customers(limit=limit)
