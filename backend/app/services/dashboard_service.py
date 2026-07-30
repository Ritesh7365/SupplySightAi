"""
Dashboard services — query analytics views only (never warehouse/public facts).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseError, NotFoundError
from app.core.logging import get_logger
from app.models.analytics_views import (
    CustomerPerformanceView,
    ExecutiveDashboardView,
    GeographicPerformanceView,
    ProductPerformanceView,
    SalesPerformanceView,
    ShippingPerformanceView,
)
from app.schemas.dashboard import (
    CustomerPerformanceItem,
    CustomersDashboardResponse,
    ExecutiveDashboardResponse,
    GeographicPerformanceItem,
    GeographicPerformanceResponse,
    InventoryAlertItem,
    InventoryAlertsResponse,
    ProductPerformanceItem,
    ProductPerformanceResponse,
    RecentOrderItem,
    RecentOrdersResponse,
    SalesPerformanceItem,
    SalesPerformanceResponse,
    SegmentSummaryItem,
    ShippingPerformanceItem,
    ShippingPerformanceResponse,
)
from app.utils.pagination import clamp_limit

logger = get_logger("services.dashboard")


class DashboardService:
    """Read-only dashboard aggregations from ``analytics`` views."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_executive(self) -> ExecutiveDashboardResponse:
        logger.debug("Fetching executive dashboard KPIs")
        try:
            row = self.db.execute(select(ExecutiveDashboardView)).scalars().first()
        except Exception as exc:  # noqa: BLE001 — wrapped as DatabaseError
            logger.exception("Failed to load executive dashboard")
            raise DatabaseError("Unable to load executive dashboard") from exc

        if row is None:
            raise NotFoundError("Executive dashboard view returned no data")
        return ExecutiveDashboardResponse.model_validate(row)

    def get_sales(
        self,
        *,
        year: Optional[int] = None,
        market: Optional[str] = None,
        region: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> SalesPerformanceResponse:
        lim = clamp_limit(limit, default=500, maximum=5000)
        stmt = select(SalesPerformanceView.__table__).order_by(
            SalesPerformanceView.year_number,
            SalesPerformanceView.month_number,
            SalesPerformanceView.market,
            SalesPerformanceView.region,
        )
        if year is not None:
            stmt = stmt.where(SalesPerformanceView.year_number == year)
        if market:
            stmt = stmt.where(SalesPerformanceView.market == market)
        if region:
            stmt = stmt.where(SalesPerformanceView.region == region)
        stmt = stmt.limit(lim)

        try:
            rows = self.db.execute(stmt).mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load sales performance")
            raise DatabaseError("Unable to load sales performance") from exc

        data = [SalesPerformanceItem.model_validate(dict(r)) for r in rows]
        return SalesPerformanceResponse(data=data, count=len(data), limit=lim)

    def get_customers(
        self,
        *,
        segment: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> CustomersDashboardResponse:
        lim = clamp_limit(limit, default=50, maximum=500)
        stmt = (
            select(CustomerPerformanceView)
            .order_by(CustomerPerformanceView.revenue_rank)
            .limit(lim)
        )
        if segment:
            stmt = stmt.where(CustomerPerformanceView.customer_segment == segment)

        try:
            customers = list(self.db.execute(stmt).scalars().all())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load customer performance")
            raise DatabaseError("Unable to load customer performance") from exc

        seg_stmt = (
            select(
                CustomerPerformanceView.customer_segment,
                func.count().label("customer_count"),
                func.sum(CustomerPerformanceView.revenue).label("revenue"),
                func.sum(CustomerPerformanceView.order_count).label("orders"),
            )
            .group_by(CustomerPerformanceView.customer_segment)
            .order_by(func.sum(CustomerPerformanceView.revenue).desc())
        )
        if segment:
            seg_stmt = seg_stmt.where(CustomerPerformanceView.customer_segment == segment)

        try:
            seg_rows = self.db.execute(seg_stmt).all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load customer segments")
            raise DatabaseError("Unable to load customer segments") from exc

        segments = []
        for name, customer_count, revenue, orders in seg_rows:
            rev = Decimal(revenue or 0)
            ord_count = int(orders or 0)
            segments.append(
                SegmentSummaryItem(
                    customer_segment=name,
                    customer_count=int(customer_count),
                    revenue=rev.quantize(Decimal("0.01")),
                    average_order_value=(
                        (rev / ord_count).quantize(Decimal("0.01")) if ord_count else None
                    ),
                )
            )

        items = [CustomerPerformanceItem.model_validate(c) for c in customers]
        return CustomersDashboardResponse(
            customers=items,
            segments=segments,
            count=len(items),
            limit=lim,
        )

    def get_products(
        self,
        *,
        limit: Optional[int] = None,
        lowest: bool = False,
    ) -> ProductPerformanceResponse:
        lim = clamp_limit(limit, default=50, maximum=500)
        order_col = (
            ProductPerformanceView.lowest_selling_rank
            if lowest
            else ProductPerformanceView.best_selling_rank
        )
        stmt = select(ProductPerformanceView).order_by(order_col).limit(lim)
        try:
            rows = list(self.db.execute(stmt).scalars().all())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load product performance")
            raise DatabaseError("Unable to load product performance") from exc

        data = [ProductPerformanceItem.model_validate(r) for r in rows]
        return ProductPerformanceResponse(data=data, count=len(data), limit=lim)

    def get_shipping(self) -> ShippingPerformanceResponse:
        stmt = select(ShippingPerformanceView).order_by(
            ShippingPerformanceView.late_delivery_risk_pct.desc()
        )
        try:
            rows = list(self.db.execute(stmt).scalars().all())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load shipping performance")
            raise DatabaseError("Unable to load shipping performance") from exc

        data = [ShippingPerformanceItem.model_validate(r) for r in rows]
        return ShippingPerformanceResponse(data=data, count=len(data), limit=None)

    def get_geography(
        self,
        *,
        country: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GeographicPerformanceResponse:
        lim = clamp_limit(limit, default=100, maximum=2000)
        stmt = (
            select(GeographicPerformanceView.__table__)
            .order_by(GeographicPerformanceView.geo_sales_rank)
            .limit(lim)
        )
        if country:
            stmt = stmt.where(GeographicPerformanceView.country == country)

        try:
            rows = self.db.execute(stmt).mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load geographic performance")
            raise DatabaseError("Unable to load geographic performance") from exc

        data = [GeographicPerformanceItem.model_validate(dict(r)) for r in rows]
        return GeographicPerformanceResponse(data=data, count=len(data), limit=lim)

    def get_recent_orders(self, *, limit: Optional[int] = None) -> RecentOrdersResponse:
        """Latest orders with revenue from warehouse facts + public order status."""
        lim = clamp_limit(limit, default=10, maximum=50)
        sql = text(
            """
            SELECT
                o.order_id,
                TRIM(
                    CONCAT(COALESCE(c.first_name, ''), ' ', COALESCE(c.last_name, ''))
                ) AS customer_name,
                ROUND(SUM(fs.sales), 2) AS revenue,
                o.order_status AS status,
                o.order_date
            FROM warehouse.fact_sales fs
            INNER JOIN public.orders o
                ON o.order_id = fs.order_id
            INNER JOIN public.customers c
                ON c.customer_id = o.customer_id
            GROUP BY
                o.order_id,
                c.first_name,
                c.last_name,
                o.order_status,
                o.order_date
            ORDER BY o.order_date DESC
            LIMIT :limit
            """
        )
        try:
            rows = self.db.execute(sql, {"limit": lim}).mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load recent orders")
            raise DatabaseError("Unable to load recent orders") from exc

        data = [RecentOrderItem.model_validate(dict(r)) for r in rows]
        return RecentOrdersResponse(data=data, count=len(data), limit=lim)

    def get_inventory_alerts(self, *, limit: Optional[int] = None) -> InventoryAlertsResponse:
        """
        Inventory alerts from public.inventory.

        Categories:
        - out_of_stock: available <= 0
        - low_stock: available > 0 and available <= reorder_point
        - reorder_soon: available > reorder_point and available <= reorder_point * 1.25
        """
        lim = clamp_limit(limit, default=20, maximum=100)
        sql = text(
            """
            SELECT
                i.inventory_id,
                i.product_id,
                p.product_name,
                i.warehouse_id,
                i.quantity_available,
                i.reorder_point,
                CASE
                    WHEN i.quantity_available <= 0 THEN 'out_of_stock'
                    WHEN i.reorder_point IS NOT NULL
                         AND i.quantity_available <= i.reorder_point THEN 'low_stock'
                    WHEN i.reorder_point IS NOT NULL
                         AND i.quantity_available <= (i.reorder_point * 1.25) THEN 'reorder_soon'
                    ELSE NULL
                END AS alert_type
            FROM public.inventory i
            INNER JOIN public.products p
                ON p.product_id = i.product_id
            WHERE
                i.quantity_available <= 0
                OR (
                    i.reorder_point IS NOT NULL
                    AND i.quantity_available <= (i.reorder_point * 1.25)
                )
            ORDER BY
                CASE
                    WHEN i.quantity_available <= 0 THEN 0
                    WHEN i.reorder_point IS NOT NULL
                         AND i.quantity_available <= i.reorder_point THEN 1
                    ELSE 2
                END,
                i.quantity_available ASC
            LIMIT :limit
            """
        )
        try:
            rows = self.db.execute(sql, {"limit": lim}).mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load inventory alerts")
            raise DatabaseError("Unable to load inventory alerts") from exc

        data = [InventoryAlertItem.model_validate(dict(r)) for r in rows]
        return InventoryAlertsResponse(
            data=data,
            count=len(data),
            limit=lim,
            out_of_stock_count=sum(1 for r in data if r.alert_type == "out_of_stock"),
            low_stock_count=sum(1 for r in data if r.alert_type == "low_stock"),
            reorder_soon_count=sum(1 for r in data if r.alert_type == "reorder_soon"),
        )
