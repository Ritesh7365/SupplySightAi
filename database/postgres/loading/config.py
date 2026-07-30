"""
Load pipeline configuration: table order, PK columns, CSV paths.
"""

from __future__ import annotations

from pathlib import Path

# Resolve paths without importing connection (avoids circular / path issues)
_LOADING_DIR = Path(__file__).resolve().parent
_POSTGRES_DIR = _LOADING_DIR.parent
_DATABASE_DIR = _POSTGRES_DIR.parent
_PROJECT_ROOT = _DATABASE_DIR.parent

TARGET_SCHEMA: str = "public"

# FK-safe load order (as specified)
LOAD_ORDER: tuple[str, ...] = (
    "departments",
    "categories",
    "products",
    "customers",
    "orders",
    "order_items",
    "shipments",
    "warehouses",
    "vendors",
    "inventory",
    "vendor_products",
)

TRUNCATE_ORDER: tuple[str, ...] = tuple(reversed(LOAD_ORDER))

PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "departments": ("department_id",),
    "categories": ("category_id",),
    "products": ("product_id",),
    "customers": ("customer_id",),
    "orders": ("order_id",),
    "order_items": ("order_item_id",),
    "shipments": ("shipment_id",),
    "warehouses": ("warehouse_id",),
    "vendors": ("vendor_id",),
    "inventory": ("inventory_id",),
    "vendor_products": ("vendor_product_id",),
}

ALLOW_EMPTY: frozenset[str] = frozenset(
    {"warehouses", "vendors", "inventory", "vendor_products"}
)

VENDOR_PRODUCTS_HEADERS: tuple[str, ...] = (
    "vendor_product_id",
    "vendor_id",
    "product_id",
    "vendor_sku",
    "lead_time_days",
    "unit_cost",
    "is_preferred",
    "created_at",
    "updated_at",
)

CSV_DIR: Path = _DATABASE_DIR / "normalized_data"
LOAD_REPORT_PATH: Path = _POSTGRES_DIR / "reports" / "load_report.md"
LOG_DIR: Path = _POSTGRES_DIR / "logs"
