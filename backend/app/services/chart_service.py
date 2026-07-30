"""
Chart services — series data from analytics views / materialized views.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseError
from app.core.logging import get_logger
from app.models.analytics_views import (
    CustomerPerformanceView,
    MonthlySalesMatView,
    ProductPerformanceView,
)
from app.schemas.charts import (
    MonthlySalesChartResponse,
    MonthlySalesPoint,
    TopCustomerPoint,
    TopCustomersChartResponse,
    TopProductPoint,
    TopProductsChartResponse,
)
from app.utils.pagination import clamp_limit

logger = get_logger("services.charts")


class ChartService:
    """Chart-oriented read models from the analytics layer."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def monthly_sales(self, *, year: Optional[int] = None) -> MonthlySalesChartResponse:
        stmt = select(MonthlySalesMatView).order_by(
            MonthlySalesMatView.year_number,
            MonthlySalesMatView.month_number,
        )
        if year is not None:
            stmt = stmt.where(MonthlySalesMatView.year_number == year)

        try:
            rows = list(self.db.execute(stmt).scalars().all())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load monthly sales chart")
            raise DatabaseError("Unable to load monthly sales chart") from exc

        data = [MonthlySalesPoint.model_validate(r) for r in rows]
        return MonthlySalesChartResponse(data=data, count=len(data), limit=None)

    def top_products(self, *, limit: Optional[int] = None) -> TopProductsChartResponse:
        lim = clamp_limit(limit, default=10, maximum=100)
        stmt = (
            select(ProductPerformanceView)
            .order_by(ProductPerformanceView.best_selling_rank)
            .limit(lim)
        )
        try:
            rows = list(self.db.execute(stmt).scalars().all())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load top products chart")
            raise DatabaseError("Unable to load top products chart") from exc

        data = [
            TopProductPoint(
                product_id=r.product_id,
                product_name=r.product_name,
                category_name=r.category_name,
                department_name=r.department_name,
                sales=r.sales,
                profit=r.profit,
                units_sold=r.units_sold,
                best_selling_rank=r.best_selling_rank,
                profit_margin_pct=r.profit_margin_pct,
            )
            for r in rows
        ]
        return TopProductsChartResponse(data=data, count=len(data), limit=lim)

    def top_customers(self, *, limit: Optional[int] = None) -> TopCustomersChartResponse:
        lim = clamp_limit(limit, default=10, maximum=100)
        stmt = (
            select(CustomerPerformanceView)
            .order_by(CustomerPerformanceView.revenue_rank)
            .limit(lim)
        )
        try:
            rows = list(self.db.execute(stmt).scalars().all())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load top customers chart")
            raise DatabaseError("Unable to load top customers chart") from exc

        data = [
            TopCustomerPoint(
                customer_id=r.customer_id,
                customer_name=r.customer_name,
                customer_segment=r.customer_segment,
                revenue=r.revenue,
                profit=r.profit,
                order_count=r.order_count,
                average_order_value=r.average_order_value,
                revenue_rank=r.revenue_rank,
            )
            for r in rows
        ]
        return TopCustomersChartResponse(data=data, count=len(data), limit=lim)
