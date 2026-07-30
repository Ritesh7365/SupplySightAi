"""Pydantic schemas package."""

from app.schemas.charts import (
    MonthlySalesChartResponse,
    TopCustomersChartResponse,
    TopProductsChartResponse,
)
from app.schemas.common import HealthResponse
from app.schemas.dashboard import (
    CustomersDashboardResponse,
    ExecutiveDashboardResponse,
    GeographicPerformanceResponse,
    ProductPerformanceResponse,
    SalesPerformanceResponse,
    ShippingPerformanceResponse,
)

__all__ = [
    "CustomersDashboardResponse",
    "ExecutiveDashboardResponse",
    "GeographicPerformanceResponse",
    "HealthResponse",
    "MonthlySalesChartResponse",
    "ProductPerformanceResponse",
    "SalesPerformanceResponse",
    "ShippingPerformanceResponse",
    "TopCustomersChartResponse",
    "TopProductsChartResponse",
]
