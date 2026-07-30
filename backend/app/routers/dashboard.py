"""Dashboard REST routers — backed by analytics views."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.core.deps import DbSession, OptionalUser
from app.schemas.common import OPENAPI_ERROR_RESPONSES
from app.schemas.dashboard import (
    CustomersDashboardResponse,
    ExecutiveDashboardResponse,
    GeographicPerformanceResponse,
    InventoryAlertsResponse,
    NamedMetricResponse,
    ProductPerformanceResponse,
    RecentOrdersResponse,
    RecentShipmentsResponse,
    SalesPerformanceResponse,
    ShippingPerformanceResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses=OPENAPI_ERROR_RESPONSES,
)


@router.get(
    "/executive",
    response_model=ExecutiveDashboardResponse,
    summary="Executive dashboard KPIs",
    description=(
        "Returns enterprise totals from ``analytics.vw_executive_dashboard``: "
        "sales, profit, orders, customers, AOV, and late delivery %."
    ),
)
def get_executive_dashboard(
    db: DbSession,
    _user: OptionalUser,
) -> ExecutiveDashboardResponse:
    return DashboardService(db).get_executive()


@router.get(
    "/sales",
    response_model=SalesPerformanceResponse,
    summary="Sales performance dashboard",
    description=(
        "Sales by month/year/region/market from ``analytics.vw_sales_performance``. "
        "Optional filters: year, market, region."
    ),
)
def get_sales_dashboard(
    db: DbSession,
    _user: OptionalUser,
    year: Optional[int] = Query(default=None, ge=2000, le=2100),
    market: Optional[str] = Query(default=None, max_length=50),
    region: Optional[str] = Query(default=None, max_length=100),
    limit: Optional[int] = Query(default=500, ge=1, le=5000),
) -> SalesPerformanceResponse:
    return DashboardService(db).get_sales(
        year=year,
        market=market,
        region=region,
        limit=limit,
    )


@router.get(
    "/customers",
    response_model=CustomersDashboardResponse,
    summary="Customer performance dashboard",
    description=(
        "Top customers, revenue, AOV, and segment rollups from "
        "``analytics.vw_customer_performance``."
    ),
)
def get_customers_dashboard(
    db: DbSession,
    _user: OptionalUser,
    segment: Optional[str] = Query(
        default=None,
        description="Filter by customer segment (Consumer, Corporate, Home Office)",
        max_length=50,
    ),
    limit: Optional[int] = Query(default=50, ge=1, le=500),
) -> CustomersDashboardResponse:
    return DashboardService(db).get_customers(segment=segment, limit=limit)


@router.get(
    "/products",
    response_model=ProductPerformanceResponse,
    summary="Product performance dashboard",
    description=(
        "Best or lowest selling products with category/department attributes from "
        "``analytics.vw_product_performance``."
    ),
)
def get_products_dashboard(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=50, ge=1, le=500),
    lowest: bool = Query(
        default=False,
        description="If true, order by lowest_selling_rank instead of best_selling_rank",
    ),
) -> ProductPerformanceResponse:
    return DashboardService(db).get_products(limit=limit, lowest=lowest)


@router.get(
    "/shipping",
    response_model=ShippingPerformanceResponse,
    summary="Shipping performance dashboard",
    description=(
        "Shipping mode KPIs: delays, late delivery risk, average transit days from "
        "``analytics.vw_shipping_performance``."
    ),
)
def get_shipping_dashboard(
    db: DbSession,
    _user: OptionalUser,
) -> ShippingPerformanceResponse:
    return DashboardService(db).get_shipping()


@router.get(
    "/geography",
    response_model=GeographicPerformanceResponse,
    summary="Geographic performance dashboard",
    description=(
        "Sales by country/state/city from ``analytics.vw_geographic_performance``."
    ),
)
def get_geography_dashboard(
    db: DbSession,
    _user: OptionalUser,
    country: Optional[str] = Query(default=None, max_length=100),
    limit: Optional[int] = Query(default=100, ge=1, le=2000),
) -> GeographicPerformanceResponse:
    return DashboardService(db).get_geography(country=country, limit=limit)


@router.get(
    "/recent-orders",
    response_model=RecentOrdersResponse,
    summary="Recent orders",
    description="Latest orders with revenue and status for the executive dashboard table.",
)
def get_recent_orders(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=10, ge=1, le=50),
) -> RecentOrdersResponse:
    return DashboardService(db).get_recent_orders(limit=limit)


@router.get(
    "/inventory-alerts",
    response_model=InventoryAlertsResponse,
    summary="Inventory alerts",
    description=(
        "Low stock / out of stock / reorder-soon alerts from public.inventory. "
        "Returns an empty list when inventory has not been populated."
    ),
)
def get_inventory_alerts(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=20, ge=1, le=100),
) -> InventoryAlertsResponse:
    return DashboardService(db).get_inventory_alerts(limit=limit)


@router.get(
    "/recent-shipments",
    response_model=RecentShipmentsResponse,
    summary="Recent shipments",
    description="Latest shipments with mode, status, and late-delivery flag.",
)
def get_recent_shipments(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=10, ge=1, le=50),
) -> RecentShipmentsResponse:
    return DashboardService(db).get_recent_shipments(limit=limit)


@router.get(
    "/revenue-by-category",
    response_model=NamedMetricResponse,
    summary="Revenue by category",
    description="Category rollup from analytics.vw_product_performance.",
)
def get_revenue_by_category(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=12, ge=1, le=50),
) -> NamedMetricResponse:
    return DashboardService(db).get_revenue_by_category(limit=limit)


@router.get(
    "/revenue-by-department",
    response_model=NamedMetricResponse,
    summary="Revenue by department",
    description="Department rollup from analytics.vw_product_performance.",
)
def get_revenue_by_department(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=12, ge=1, le=50),
) -> NamedMetricResponse:
    return DashboardService(db).get_revenue_by_department(limit=limit)
