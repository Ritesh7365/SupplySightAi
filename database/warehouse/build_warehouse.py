"""
SupplySight AI — Build and populate the warehouse star schema.

Applies CREATE TABLE scripts under database/warehouse/schema/, then
INSERT...SELECT ETL scripts under database/warehouse/etl/ from public.*.

Does not modify public tables. Does not read raw CSV.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_WAREHOUSE_DIR = Path(__file__).resolve().parent
_POSTGRES_DIR = _WAREHOUSE_DIR.parent / "postgres"
if str(_POSTGRES_DIR) not in sys.path:
    sys.path.insert(0, str(_POSTGRES_DIR))

from connection import (  # noqa: E402
    get_connection,
    get_cursor,
    list_sql_files,
    run_sql_file,
    setup_module_logging,
    table_exists,
)

logger = logging.getLogger("supplysight.warehouse.build")

SCHEMA_DIR = _WAREHOUSE_DIR / "schema"
ETL_DIR = _WAREHOUSE_DIR / "etl"

WAREHOUSE_TABLES: tuple[str, ...] = (
    "dim_date",
    "dim_department",
    "dim_category",
    "dim_product",
    "dim_customer",
    "dim_location",
    "dim_shipping",
    "fact_sales",
    "fact_shipments",
)


def apply_ddl() -> list[str]:
    """Create warehouse tables and indexes."""
    files = list_sql_files(SCHEMA_DIR)
    if not files:
        raise FileNotFoundError(f"No SQL files in {SCHEMA_DIR}")

    executed: list[str] = []
    with get_connection(autocommit=False) as conn:
        for path in files:
            logger.info("DDL: %s", path.name)
            run_sql_file(path, conn=conn)
            executed.append(path.name)
        conn.commit()
    return executed


def run_etl(*, full_refresh: bool = False) -> list[str]:
    """Populate warehouse tables from public via INSERT...SELECT scripts."""
    files = list_sql_files(ETL_DIR)
    # Skip validate here; run separately for readable result sets
    load_files = [p for p in files if not p.name.startswith("10_")]

    if not full_refresh:
        load_files = [p for p in load_files if not p.name.startswith("00_")]

    if not load_files:
        raise FileNotFoundError(f"No ETL load files in {ETL_DIR}")

    executed: list[str] = []
    with get_connection(autocommit=False) as conn:
        for path in load_files:
            logger.info("ETL: %s", path.name)
            run_sql_file(path, conn=conn)
            executed.append(path.name)
        conn.commit()
    return executed


def validate_warehouse() -> dict[str, int]:
    """Return warehouse table row counts and reconcile against public grain."""
    counts: dict[str, int] = {}
    with get_connection(autocommit=True) as conn:
        with get_cursor(conn) as cur:
            for table in WAREHOUSE_TABLES:
                cur.execute(f"SELECT COUNT(*) FROM warehouse.{table}")
                counts[table] = int(cur.fetchone()[0])

            cur.execute("SELECT COUNT(*) FROM public.order_items")
            public_items = int(cur.fetchone()[0])
            cur.execute("SELECT COUNT(*) FROM public.shipments")
            public_shipments = int(cur.fetchone()[0])
            cur.execute("SELECT COUNT(*) FROM public.customers")
            public_customers = int(cur.fetchone()[0])
            cur.execute("SELECT COUNT(*) FROM public.products")
            public_products = int(cur.fetchone()[0])

            cur.execute(
                """
                SELECT COUNT(*) FROM warehouse.fact_sales f
                LEFT JOIN warehouse.dim_date d ON d.date_key = f.date_key
                WHERE d.date_key IS NULL
                """
            )
            orphan_dates = int(cur.fetchone()[0])

    counts["_public_order_items"] = public_items
    counts["_public_shipments"] = public_shipments
    counts["_public_customers"] = public_customers
    counts["_public_products"] = public_products
    counts["_orphan_fact_sales_dates"] = orphan_dates

    logger.info("Warehouse row counts: %s", {k: v for k, v in counts.items() if not k.startswith("_")})
    logger.info(
        "Reconcile fact_sales=%s vs order_items=%s | fact_shipments=%s vs shipments=%s",
        counts["fact_sales"],
        public_items,
        counts["fact_shipments"],
        public_shipments,
    )
    if counts["fact_sales"] != public_items:
        logger.warning("fact_sales count does not match public.order_items")
    if counts["fact_shipments"] != public_shipments:
        logger.warning("fact_shipments count does not match public.shipments")
    if orphan_dates:
        logger.error("Orphan date_key rows in fact_sales: %s", orphan_dates)

    return counts


def verify_tables_exist() -> dict[str, bool]:
    presence: dict[str, bool] = {}
    with get_connection(autocommit=True) as conn:
        for table in WAREHOUSE_TABLES:
            presence[table] = table_exists("warehouse", table, conn=conn)
            logger.info(
                "warehouse.%s: %s",
                table,
                "OK" if presence[table] else "MISSING",
            )
    return presence


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SupplySight AI warehouse star schema")
    parser.add_argument("--ddl-only", action="store_true", help="Create tables/indexes only")
    parser.add_argument("--etl-only", action="store_true", help="Run ETL only")
    parser.add_argument(
        "--full-refresh",
        action="store_true",
        help="Truncate warehouse tables before ETL load",
    )
    parser.add_argument("--skip-validate", action="store_true", help="Skip post-load validation")
    args = parser.parse_args()

    setup_module_logging()
    logger.info("Warehouse build starting (schema=%s, etl=%s)", SCHEMA_DIR, ETL_DIR)

    try:
        if not args.etl_only:
            apply_ddl()
            presence = verify_tables_exist()
            if not all(presence.values()):
                missing = [t for t, ok in presence.items() if not ok]
                logger.error("Missing warehouse tables: %s", missing)
                return 1

        if not args.ddl_only:
            run_etl(full_refresh=args.full_refresh)
            if not args.skip_validate:
                counts = validate_warehouse()
                if counts["fact_sales"] != counts["_public_order_items"]:
                    return 2
                if counts["fact_shipments"] != counts["_public_shipments"]:
                    return 2
                if counts["_orphan_fact_sales_dates"]:
                    return 2

        logger.info("Warehouse build completed successfully")
        return 0
    except Exception:
        logger.exception("Warehouse build failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
