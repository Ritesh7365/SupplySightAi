"""Pydantic response models for chart endpoints."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from backend.app.schemas.common import ListResponse, ORMModel


class MonthlySalesPoint(ORMModel):
    """Time-series point from analytics.mv_monthly_sales."""

    year_number: int
    month_number: int
    year_month: str
    month_name: str
    quarter_number: int
    quarter_name: str
    sales: Decimal
    profit: Decimal
    discount: Decimal
    units_sold: int
    order_count: int
    customer_count: int
    average_order_value: Optional[Decimal] = None
    profit_margin_pct: Optional[Decimal] = None


class MonthlySalesChartResponse(ListResponse[MonthlySalesPoint]):
    data: List[MonthlySalesPoint]


class TopProductPoint(ORMModel):
    product_id: int
    product_name: str
    category_name: str
    department_name: str
    sales: Decimal
    profit: Decimal
    units_sold: int
    best_selling_rank: int
    profit_margin_pct: Optional[Decimal] = None


class TopProductsChartResponse(ListResponse[TopProductPoint]):
    data: List[TopProductPoint]


class TopCustomerPoint(ORMModel):
    customer_id: int
    customer_name: str
    customer_segment: str
    revenue: Decimal
    profit: Decimal
    order_count: int
    average_order_value: Optional[Decimal] = None
    revenue_rank: int


class TopCustomersChartResponse(ListResponse[TopCustomerPoint]):
    data: List[TopCustomerPoint]
