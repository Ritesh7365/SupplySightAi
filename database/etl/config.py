"""
SupplySight AI — ETL configuration.

Central paths, encodings, and validation expectations for the DataCo
normalization pipeline. No PostgreSQL connection settings in this phase.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
ETL_DIR: Path = Path(__file__).resolve().parent
DATABASE_DIR: Path = ETL_DIR.parent
PROJECT_ROOT: Path = DATABASE_DIR.parent

RAW_DATA_PATH: Path = (
    PROJECT_ROOT / "data" / "raw" / "data" / "DataCoSupplyChainDataset.csv"
)
NORMALIZED_DATA_DIR: Path = DATABASE_DIR / "normalized_data"
LOG_DIR: Path = ETL_DIR / "logs"

# ---------------------------------------------------------------------------
# Extract settings
# ---------------------------------------------------------------------------
CSV_ENCODING: str = "latin-1"
EXPECTED_COLUMN_COUNT: int = 53
# Soft expectation for observability (DataCo reference size); not a hard fail.
EXPECTED_MIN_ROW_COUNT: int = 1

# ---------------------------------------------------------------------------
# Output table names → CSV filenames
# ---------------------------------------------------------------------------
POPULATED_TABLES: tuple[str, ...] = (
    "departments",
    "categories",
    "products",
    "customers",
    "orders",
    "order_items",
    "shipments",
)

# Placeholder tables: headers only (no DataCo business rows)
PLACEHOLDER_TABLES: dict[str, tuple[str, ...]] = {
    "warehouses": (
        "warehouse_id",
        "warehouse_code",
        "warehouse_name",
        "city",
        "state_code",
        "country",
        "postal_code",
        "latitude",
        "longitude",
        "is_active",
        "created_at",
        "updated_at",
    ),
    "inventory": (
        "inventory_id",
        "warehouse_id",
        "product_id",
        "quantity_on_hand",
        "quantity_reserved",
        # quantity_available is GENERATED in Postgres — omitted from load CSV
        "reorder_point",
        "reorder_quantity",
        "as_of_ts",
        "created_at",
        "updated_at",
    ),
    "vendors": (
        "vendor_id",
        "vendor_code",
        "vendor_name",
        "contact_email",
        "contact_phone",
        "country",
        "city",
        "risk_tier",
        "is_active",
        "created_at",
        "updated_at",
    ),
}

LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
