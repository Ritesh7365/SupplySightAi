"""Operations services — inventory / warehouse / vendor analytics."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseError
from app.core.logging import get_logger
from app.schemas.operations import (
    InventoryBalanceItem,
    InventoryBalancesResponse,
    InventorySummaryResponse,
    VendorItem,
    VendorsResponse,
    WarehouseItem,
    WarehousesResponse,
)
from app.utils.pagination import clamp_limit

logger = get_logger("services.operations")


def _dec(value: object) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value))


class OperationsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def inventory_summary(self) -> InventorySummaryResponse:
        try:
            row = self.db.execute(
                text(
                    """
                    SELECT
                        COUNT(*)::int AS sku_count,
                        COALESCE(SUM(quantity_available), 0) AS total_units,
                        COALESCE(SUM(inventory_value), 0) AS inventory_value_proxy,
                        COUNT(*) FILTER (WHERE stock_status = 'out_of_stock')::int
                            AS out_of_stock_count,
                        COUNT(*) FILTER (WHERE stock_status = 'low_stock')::int
                            AS low_stock_count,
                        COUNT(*) FILTER (WHERE stock_status = 'below_safety')::int
                            AS below_safety_count,
                        COUNT(DISTINCT warehouse_id)::int AS warehouse_count,
                        MAX(inventory_value) AS top_inventory_value
                    FROM analytics.vw_inventory_performance
                    """
                )
            ).mappings().first()

            util = self.db.execute(
                text(
                    """
                    SELECT ROUND(AVG(utilization_pct), 2) AS avg_util
                    FROM analytics.vw_warehouse_performance
                    WHERE utilization_pct IS NOT NULL
                    """
                )
            ).scalar()

            # Turnover proxy: annualized sales units / average on-hand units
            turnover = self.db.execute(
                text(
                    """
                    WITH sales AS (
                        SELECT COALESCE(SUM(oi.quantity), 0)::numeric AS units_sold
                        FROM public.order_items oi
                    ),
                    stock AS (
                        SELECT COALESCE(AVG(quantity_on_hand), 0)::numeric AS avg_on_hand
                        FROM public.inventory
                        WHERE quantity_on_hand > 0
                    )
                    SELECT
                        CASE
                            WHEN stock.avg_on_hand = 0 THEN NULL
                            ELSE ROUND(sales.units_sold / stock.avg_on_hand, 2)
                        END
                    FROM sales, stock
                    """
                )
            ).scalar()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed inventory summary")
            raise DatabaseError("Unable to load inventory summary") from exc

        return InventorySummaryResponse(
            sku_count=int(row["sku_count"] or 0) if row else 0,
            total_units=_dec(row["total_units"]) or Decimal("0"),
            inventory_value_proxy=_dec(row["inventory_value_proxy"]) if row else None,
            out_of_stock_count=int(row["out_of_stock_count"] or 0) if row else 0,
            low_stock_count=int(row["low_stock_count"] or 0) if row else 0,
            below_safety_count=int(row["below_safety_count"] or 0) if row else 0,
            warehouse_count=int(row["warehouse_count"] or 0) if row else 0,
            inventory_turnover=_dec(turnover),
            avg_warehouse_utilization_pct=_dec(util),
            top_inventory_value=_dec(row["top_inventory_value"]) if row else None,
        )

    def inventory_balances(self, *, limit: Optional[int] = None) -> InventoryBalancesResponse:
        lim = clamp_limit(limit, default=100, maximum=500)
        try:
            rows = self.db.execute(
                text(
                    """
                    SELECT
                        inventory_id,
                        warehouse_id,
                        warehouse_name,
                        product_id,
                        product_name,
                        quantity_on_hand,
                        quantity_available,
                        reorder_point,
                        safety_stock,
                        maximum_stock,
                        inventory_value,
                        stock_status
                    FROM analytics.vw_inventory_performance
                    ORDER BY
                        CASE stock_status
                            WHEN 'out_of_stock' THEN 0
                            WHEN 'low_stock' THEN 1
                            WHEN 'below_safety' THEN 2
                            ELSE 3
                        END,
                        quantity_available ASC
                    LIMIT :limit
                    """
                ),
                {"limit": lim},
            ).mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed inventory balances")
            raise DatabaseError("Unable to load inventory balances") from exc

        data = [InventoryBalanceItem.model_validate(dict(r)) for r in rows]
        return InventoryBalancesResponse(data=data, count=len(data), limit=lim)

    def warehouses(self) -> WarehousesResponse:
        try:
            rows = self.db.execute(
                text(
                    """
                    SELECT
                        warehouse_id,
                        warehouse_code,
                        warehouse_name,
                        warehouse_type,
                        city,
                        state_code,
                        country,
                        latitude,
                        longitude,
                        is_active,
                        capacity,
                        products_stored AS sku_count,
                        products_stored,
                        units_on_hand,
                        inventory_value,
                        utilization_pct,
                        occupancy_pct,
                        COALESCE(orders_handled_proxy, 0) AS orders_handled
                    FROM analytics.vw_warehouse_performance
                    ORDER BY inventory_value DESC NULLS LAST, warehouse_name
                    """
                )
            ).mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed warehouses list")
            raise DatabaseError("Unable to load warehouses") from exc

        data = [WarehouseItem.model_validate(dict(r)) for r in rows]
        capacities = [d.capacity for d in data if d.capacity is not None]
        utils = [d.utilization_pct for d in data if d.utilization_pct is not None]
        values = [d.inventory_value for d in data if d.inventory_value is not None]
        return WarehousesResponse(
            data=data,
            count=len(data),
            limit=None,
            warehouse_count=len(data),
            total_capacity=sum(capacities, Decimal("0")) if capacities else None,
            avg_utilization_pct=(
                (sum(utils, Decimal("0")) / len(utils)).quantize(Decimal("0.01"))
                if utils
                else None
            ),
            total_inventory_value=sum(values, Decimal("0")) if values else None,
        )

    def vendors(self) -> VendorsResponse:
        try:
            rows = self.db.execute(
                text(
                    """
                    SELECT
                        vendor_id,
                        vendor_code,
                        vendor_name,
                        country,
                        city,
                        risk_tier,
                        is_active,
                        product_count,
                        COALESCE(avg_product_lead_time_days, vendor_lead_time_days)
                            AS avg_lead_time_days,
                        rating,
                        on_time_delivery_pct,
                        purchase_volume_proxy,
                        CASE
                            WHEN on_time_delivery_pct IS NULL THEN NULL
                            ELSE ROUND(100 - on_time_delivery_pct, 2)
                        END AS late_delivery_pct
                    FROM analytics.vw_vendor_performance
                    ORDER BY purchase_volume_proxy DESC NULLS LAST, vendor_name
                    """
                )
            ).mappings().all()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed vendors list")
            raise DatabaseError("Unable to load vendors") from exc

        data = [VendorItem.model_validate(dict(r)) for r in rows]
        leads = [v.avg_lead_time_days for v in data if v.avg_lead_time_days is not None]
        ratings = [v.rating for v in data if v.rating is not None]
        on_times = [v.on_time_delivery_pct for v in data if v.on_time_delivery_pct is not None]
        volumes = [v.purchase_volume_proxy for v in data if v.purchase_volume_proxy is not None]

        return VendorsResponse(
            data=data,
            count=len(data),
            limit=None,
            vendor_count=len(data),
            avg_lead_time_days=(
                (sum(leads, Decimal("0")) / len(leads)).quantize(Decimal("0.01"))
                if leads
                else None
            ),
            avg_rating=(
                (sum(ratings, Decimal("0")) / len(ratings)).quantize(Decimal("0.01"))
                if ratings
                else None
            ),
            on_time_pct=(
                (sum(on_times, Decimal("0")) / len(on_times)).quantize(Decimal("0.01"))
                if on_times
                else None
            ),
            total_purchase_volume=sum(volumes, Decimal("0")) if volumes else None,
        )
