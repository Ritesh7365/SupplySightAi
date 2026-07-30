"""Operations schemas — inventory, warehouses, vendors."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from app.schemas.common import ListResponse, ORMModel


class InventorySummaryResponse(ORMModel):
    sku_count: int = 0
    total_units: Decimal = Decimal("0")
    inventory_value_proxy: Optional[Decimal] = None
    low_stock_count: int = 0
    out_of_stock_count: int = 0
    below_safety_count: int = 0
    warehouse_count: int = 0
    inventory_turnover: Optional[Decimal] = None
    avg_warehouse_utilization_pct: Optional[Decimal] = None
    top_inventory_value: Optional[Decimal] = None


class InventoryBalanceItem(ORMModel):
    inventory_id: int
    warehouse_id: int
    warehouse_name: Optional[str] = None
    product_id: int
    product_name: str
    quantity_on_hand: Decimal
    quantity_available: Decimal
    reorder_point: Optional[Decimal] = None
    safety_stock: Optional[Decimal] = None
    maximum_stock: Optional[Decimal] = None
    inventory_value: Optional[Decimal] = None
    stock_status: Optional[str] = None


class InventoryBalancesResponse(ListResponse[InventoryBalanceItem]):
    data: List[InventoryBalanceItem]


class WarehouseItem(ORMModel):
    warehouse_id: int
    warehouse_code: str
    warehouse_name: str
    warehouse_type: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_active: bool = True
    capacity: Optional[Decimal] = None
    sku_count: int = 0
    products_stored: int = 0
    units_on_hand: Decimal = Decimal("0")
    inventory_value: Optional[Decimal] = None
    utilization_pct: Optional[Decimal] = None
    occupancy_pct: Optional[Decimal] = None
    orders_handled: int = 0


class WarehousesResponse(ListResponse[WarehouseItem]):
    data: List[WarehouseItem]
    warehouse_count: int = 0
    total_capacity: Optional[Decimal] = None
    avg_utilization_pct: Optional[Decimal] = None
    total_inventory_value: Optional[Decimal] = None


class VendorItem(ORMModel):
    vendor_id: int
    vendor_code: str
    vendor_name: str
    country: Optional[str] = None
    city: Optional[str] = None
    risk_tier: Optional[str] = None
    is_active: bool = True
    product_count: int = 0
    avg_lead_time_days: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    on_time_delivery_pct: Optional[Decimal] = None
    purchase_volume_proxy: Optional[Decimal] = None
    late_delivery_pct: Optional[Decimal] = None


class VendorsResponse(ListResponse[VendorItem]):
    data: List[VendorItem]
    vendor_count: int = 0
    avg_lead_time_days: Optional[Decimal] = None
    avg_rating: Optional[Decimal] = None
    on_time_pct: Optional[Decimal] = Field(
        default=None,
        description="Average vendor on-time delivery %",
    )
    total_purchase_volume: Optional[Decimal] = None
