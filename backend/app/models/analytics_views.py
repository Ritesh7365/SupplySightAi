"""
SQLAlchemy mappings for analytics views / materialized views.

These models are read-only. Services must query ``analytics.*`` objects only —
never ``warehouse`` or ``public`` fact tables.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base

ANALYTICS_SCHEMA = "analytics"


class ExecutiveDashboardView(Base):
    """analytics.vw_executive_dashboard — single KPI row."""

    __tablename__ = "vw_executive_dashboard"
    __table_args__ = {"schema": ANALYTICS_SCHEMA}

    # Views lack a natural PK; use refreshed_at as mapper identity for ORM loads.
    refreshed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    total_sales: Mapped[Decimal] = mapped_column(Numeric)
    total_profit: Mapped[Decimal] = mapped_column(Numeric)
    total_orders: Mapped[int] = mapped_column(BigInteger)
    total_customers: Mapped[int] = mapped_column(BigInteger)
    average_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    late_delivery_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    total_shipments: Mapped[int] = mapped_column(BigInteger)
    late_shipments: Mapped[int] = mapped_column(BigInteger)
    overall_profit_margin_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)


class SalesPerformanceView(Base):
    """analytics.vw_sales_performance."""

    __tablename__ = "vw_sales_performance"
    __table_args__ = {"schema": ANALYTICS_SCHEMA}

    year_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    month_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    year_month: Mapped[str] = mapped_column(String(7))
    month_name: Mapped[str] = mapped_column(String(10))
    quarter_number: Mapped[int] = mapped_column(Integer)
    quarter_name: Mapped[str] = mapped_column(String(2))
    market: Mapped[Optional[str]] = mapped_column(String(50), primary_key=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), primary_key=True)
    sales: Mapped[Decimal] = mapped_column(Numeric)
    profit: Mapped[Decimal] = mapped_column(Numeric)
    discount: Mapped[Decimal] = mapped_column(Numeric)
    units_sold: Mapped[int] = mapped_column(BigInteger)
    order_count: Mapped[int] = mapped_column(BigInteger)
    customer_count: Mapped[int] = mapped_column(BigInteger)
    line_count: Mapped[int] = mapped_column(BigInteger)
    average_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    profit_margin_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)


class CustomerPerformanceView(Base):
    """analytics.vw_customer_performance."""

    __tablename__ = "vw_customer_performance"
    __table_args__ = {"schema": ANALYTICS_SCHEMA}

    customer_key: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer)
    customer_name: Mapped[str] = mapped_column(String)
    customer_segment: Mapped[str] = mapped_column(String(50))
    customer_city: Mapped[Optional[str]] = mapped_column(String(100))
    customer_state: Mapped[Optional[str]] = mapped_column(String(50))
    customer_country: Mapped[Optional[str]] = mapped_column(String(100))
    revenue: Mapped[Decimal] = mapped_column(Numeric)
    profit: Mapped[Decimal] = mapped_column(Numeric)
    discount: Mapped[Decimal] = mapped_column(Numeric)
    order_count: Mapped[int] = mapped_column(BigInteger)
    units_purchased: Mapped[int] = mapped_column(BigInteger)
    average_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    profit_margin_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    revenue_rank: Mapped[int] = mapped_column(BigInteger)
    segment_revenue_rank: Mapped[int] = mapped_column(BigInteger)


class ProductPerformanceView(Base):
    """analytics.vw_product_performance."""

    __tablename__ = "vw_product_performance"
    __table_args__ = {"schema": ANALYTICS_SCHEMA}

    product_key: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer)
    product_name: Mapped[str] = mapped_column(String(255))
    product_price: Mapped[Decimal] = mapped_column(Numeric)
    product_status_desc: Mapped[str] = mapped_column(String(20))
    category_key: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(Integer)
    category_name: Mapped[str] = mapped_column(String(120))
    department_key: Mapped[int] = mapped_column(BigInteger)
    department_id: Mapped[int] = mapped_column(Integer)
    department_name: Mapped[str] = mapped_column(String(100))
    sales: Mapped[Decimal] = mapped_column(Numeric)
    profit: Mapped[Decimal] = mapped_column(Numeric)
    discount: Mapped[Decimal] = mapped_column(Numeric)
    units_sold: Mapped[int] = mapped_column(BigInteger)
    order_count: Mapped[int] = mapped_column(BigInteger)
    customer_count: Mapped[int] = mapped_column(BigInteger)
    profit_margin_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    best_selling_rank: Mapped[int] = mapped_column(BigInteger)
    lowest_selling_rank: Mapped[int] = mapped_column(BigInteger)
    profit_rank: Mapped[int] = mapped_column(BigInteger)
    category_sales_rank: Mapped[int] = mapped_column(BigInteger)
    category_total_sales: Mapped[Decimal] = mapped_column(Numeric)
    category_total_profit: Mapped[Decimal] = mapped_column(Numeric)


class ShippingPerformanceView(Base):
    """analytics.vw_shipping_performance."""

    __tablename__ = "vw_shipping_performance"
    __table_args__ = {"schema": ANALYTICS_SCHEMA}

    shipping_key: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    shipping_mode: Mapped[str] = mapped_column(String(50))
    shipping_mode_group: Mapped[str] = mapped_column(String(30))
    shipment_count: Mapped[int] = mapped_column(BigInteger)
    customer_count: Mapped[int] = mapped_column(BigInteger)
    order_count: Mapped[int] = mapped_column(BigInteger)
    avg_shipping_time_days: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    avg_scheduled_days: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    avg_delivery_delay_days: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    delayed_shipment_count: Mapped[int] = mapped_column(BigInteger)
    delay_rate_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    late_delivery_count: Mapped[int] = mapped_column(BigInteger)
    late_delivery_risk_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    late_delivery_status_count: Mapped[int] = mapped_column(BigInteger)
    on_time_status_count: Mapped[int] = mapped_column(BigInteger)
    advance_shipping_count: Mapped[int] = mapped_column(BigInteger)
    canceled_shipment_count: Mapped[int] = mapped_column(BigInteger)


class GeographicPerformanceView(Base):
    """analytics.vw_geographic_performance."""

    __tablename__ = "vw_geographic_performance"
    __table_args__ = {"schema": ANALYTICS_SCHEMA}

    market: Mapped[Optional[str]] = mapped_column(String(50), primary_key=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), primary_key=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), primary_key=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), primary_key=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), primary_key=True)
    sales: Mapped[Decimal] = mapped_column(Numeric)
    profit: Mapped[Decimal] = mapped_column(Numeric)
    discount: Mapped[Decimal] = mapped_column(Numeric)
    units_sold: Mapped[int] = mapped_column(BigInteger)
    order_count: Mapped[int] = mapped_column(BigInteger)
    customer_count: Mapped[int] = mapped_column(BigInteger)
    average_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    profit_margin_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    geo_sales_rank: Mapped[int] = mapped_column(BigInteger)
    country_city_sales_rank: Mapped[int] = mapped_column(BigInteger)


class MonthlySalesMatView(Base):
    """analytics.mv_monthly_sales — chart-optimized monthly aggregates."""

    __tablename__ = "mv_monthly_sales"
    __table_args__ = {"schema": ANALYTICS_SCHEMA}

    year_month: Mapped[str] = mapped_column(String(7), primary_key=True)
    year_number: Mapped[int] = mapped_column(Integer)
    month_number: Mapped[int] = mapped_column(Integer)
    month_name: Mapped[str] = mapped_column(String(10))
    quarter_number: Mapped[int] = mapped_column(Integer)
    quarter_name: Mapped[str] = mapped_column(String(2))
    sales: Mapped[Decimal] = mapped_column(Numeric)
    profit: Mapped[Decimal] = mapped_column(Numeric)
    discount: Mapped[Decimal] = mapped_column(Numeric)
    units_sold: Mapped[int] = mapped_column(BigInteger)
    order_count: Mapped[int] = mapped_column(BigInteger)
    customer_count: Mapped[int] = mapped_column(BigInteger)
    line_count: Mapped[int] = mapped_column(BigInteger)
    average_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    profit_margin_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric)
