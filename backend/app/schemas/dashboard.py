"""Pydantic response models for dashboard endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import ConfigDict, Field

from backend.app.schemas.common import ListResponse, ORMModel


class ExecutiveDashboardResponse(ORMModel):
    """KPIs from analytics.vw_executive_dashboard."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "total_sales": "36784734.31",
                    "total_profit": "3966902.97",
                    "total_orders": 65752,
                    "total_customers": 20652,
                    "average_order_value": "559.45",
                    "late_delivery_pct": "54.82",
                    "total_shipments": 65752,
                    "late_shipments": 36048,
                    "overall_profit_margin_pct": "10.78",
                    "refreshed_at": "2026-07-30T13:00:00+05:30",
                }
            ]
        },
    )

    total_sales: Decimal
    total_profit: Decimal
    total_orders: int
    total_customers: int
    average_order_value: Optional[Decimal] = None
    late_delivery_pct: Optional[Decimal] = None
    total_shipments: int
    late_shipments: int
    overall_profit_margin_pct: Optional[Decimal] = None
    refreshed_at: datetime


class SalesPerformanceItem(ORMModel):
    year_number: int
    month_number: int
    year_month: str
    month_name: str
    quarter_number: int
    quarter_name: str
    market: Optional[str] = None
    region: Optional[str] = None
    sales: Decimal
    profit: Decimal
    discount: Decimal
    units_sold: int
    order_count: int
    customer_count: int
    line_count: int
    average_order_value: Optional[Decimal] = None
    profit_margin_pct: Optional[Decimal] = None


class SalesPerformanceResponse(ListResponse[SalesPerformanceItem]):
    data: List[SalesPerformanceItem]


class CustomerPerformanceItem(ORMModel):
    customer_key: int
    customer_id: int
    customer_name: str
    customer_segment: str
    customer_city: Optional[str] = None
    customer_state: Optional[str] = None
    customer_country: Optional[str] = None
    revenue: Decimal
    profit: Decimal
    discount: Decimal
    order_count: int
    units_purchased: int
    average_order_value: Optional[Decimal] = None
    profit_margin_pct: Optional[Decimal] = None
    revenue_rank: int
    segment_revenue_rank: int


class CustomerPerformanceResponse(ListResponse[CustomerPerformanceItem]):
    data: List[CustomerPerformanceItem]


class ProductPerformanceItem(ORMModel):
    product_key: int
    product_id: int
    product_name: str
    product_price: Decimal
    product_status_desc: str
    category_key: int
    category_id: int
    category_name: str
    department_key: int
    department_id: int
    department_name: str
    sales: Decimal
    profit: Decimal
    discount: Decimal
    units_sold: int
    order_count: int
    customer_count: int
    profit_margin_pct: Optional[Decimal] = None
    best_selling_rank: int
    lowest_selling_rank: int
    profit_rank: int
    category_sales_rank: int
    category_total_sales: Decimal
    category_total_profit: Decimal


class ProductPerformanceResponse(ListResponse[ProductPerformanceItem]):
    data: List[ProductPerformanceItem]


class ShippingPerformanceItem(ORMModel):
    shipping_key: int
    shipping_mode: str
    shipping_mode_group: str
    shipment_count: int
    customer_count: int
    order_count: int
    avg_shipping_time_days: Optional[Decimal] = None
    avg_scheduled_days: Optional[Decimal] = None
    avg_delivery_delay_days: Optional[Decimal] = None
    delayed_shipment_count: int
    delay_rate_pct: Optional[Decimal] = None
    late_delivery_count: int
    late_delivery_risk_pct: Optional[Decimal] = None
    late_delivery_status_count: int
    on_time_status_count: int
    advance_shipping_count: int
    canceled_shipment_count: int


class ShippingPerformanceResponse(ListResponse[ShippingPerformanceItem]):
    data: List[ShippingPerformanceItem]


class GeographicPerformanceItem(ORMModel):
    market: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    sales: Decimal
    profit: Decimal
    discount: Decimal
    units_sold: int
    order_count: int
    customer_count: int
    average_order_value: Optional[Decimal] = None
    profit_margin_pct: Optional[Decimal] = None
    geo_sales_rank: int
    country_city_sales_rank: int


class GeographicPerformanceResponse(ListResponse[GeographicPerformanceItem]):
    data: List[GeographicPerformanceItem]


class SegmentSummaryItem(ORMModel):
    """Optional rollup used on the customers dashboard."""

    customer_segment: str
    customer_count: int
    revenue: Decimal
    average_order_value: Optional[Decimal] = None


class CustomersDashboardResponse(ORMModel):
    """Customers dashboard: ranked list + segment rollup."""

    customers: List[CustomerPerformanceItem] = Field(default_factory=list)
    segments: List[SegmentSummaryItem] = Field(default_factory=list)
    count: int = 0
    limit: Optional[int] = None
