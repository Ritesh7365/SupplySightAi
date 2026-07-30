"""
SupplySight AI — Build analytics views and materialized views.

Creates dashboard-oriented objects in the ``analytics`` schema from
``warehouse`` star-schema tables. Does not modify warehouse or public tables.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_ANALYTICS_DIR = Path(__file__).resolve().parent
_POSTGRES_DIR = _ANALYTICS_DIR.parent / "postgres"
if str(_POSTGRES_DIR) not in sys.path:
    sys.path.insert(0, str(_POSTGRES_DIR))

from connection import (  # noqa: E402
    get_connection,
    get_cursor,
    list_sql_files,
    run_sql_file,
    setup_module_logging,
)

logger = logging.getLogger("supplysight.analytics.build")

VIEWS_DIR = _ANALYTICS_DIR / "views"
MATVIEWS_DIR = _ANALYTICS_DIR / "materialized"

ANALYTICS_VIEWS: tuple[str, ...] = (
    "vw_executive_dashboard",
    "vw_sales_performance",
    "vw_customer_performance",
    "vw_product_performance",
    "vw_shipping_performance",
    "vw_geographic_performance",
)

ANALYTICS_MATVIEWS: tuple[str, ...] = (
    "mv_monthly_sales",
    "mv_customer_sales",
    "mv_product_sales",
)


def apply_views() -> list[str]:
    files = list_sql_files(VIEWS_DIR)
    if not files:
        raise FileNotFoundError(f"No view SQL in {VIEWS_DIR}")
    executed: list[str] = []
    with get_connection(autocommit=False) as conn:
        for path in files:
            logger.info("View: %s", path.name)
            run_sql_file(path, conn=conn)
            executed.append(path.name)
        conn.commit()
    return executed


def apply_matviews() -> list[str]:
    files = list_sql_files(MATVIEWS_DIR)
    if not files:
        raise FileNotFoundError(f"No materialized view SQL in {MATVIEWS_DIR}")
    executed: list[str] = []
    # Each file DROPs/CREATEs; commit per file so indexes apply cleanly
    with get_connection(autocommit=False) as conn:
        for path in files:
            logger.info("Materialized view: %s", path.name)
            run_sql_file(path, conn=conn)
            executed.append(path.name)
        conn.commit()
    return executed


def refresh_matviews() -> None:
    with get_connection(autocommit=True) as conn:
        with get_cursor(conn) as cur:
            for name in ANALYTICS_MATVIEWS:
                sql = f"REFRESH MATERIALIZED VIEW analytics.{name};"
                logger.info("Refreshing analytics.%s", name)
                cur.execute(sql)


def _relation_exists(schema: str, name: str, *, conn) -> bool:
    """True if a table, view, or materialized view exists (to_regclass)."""
    with get_cursor(conn) as cur:
        cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"{schema}.{name}",))
        return bool(cur.fetchone()[0])


def verify() -> dict[str, object]:
    result: dict[str, object] = {"views": {}, "matviews": {}}
    with get_connection(autocommit=True) as conn:
        with get_cursor(conn) as cur:
            for name in ANALYTICS_VIEWS:
                if not _relation_exists("analytics", name, conn=conn):
                    result["views"][name] = None  # type: ignore[index]
                    logger.error("Missing analytics.%s", name)
                    continue
                cur.execute(f"SELECT COUNT(*) FROM analytics.{name}")
                result["views"][name] = cur.fetchone()[0]  # type: ignore[index]
                logger.info("analytics.%s rows: %s", name, result["views"][name])

            for name in ANALYTICS_MATVIEWS:
                if not _relation_exists("analytics", name, conn=conn):
                    result["matviews"][name] = None  # type: ignore[index]
                    logger.error("Missing analytics.%s", name)
                    continue
                cur.execute(f"SELECT COUNT(*) FROM analytics.{name}")
                cnt = cur.fetchone()[0]
                result["matviews"][name] = cnt  # type: ignore[index]
                logger.info("analytics.%s rows: %s", name, cnt)

            cur.execute("SELECT * FROM analytics.vw_executive_dashboard")
            row = cur.fetchone()
            cols = [d[0] for d in cur.description]
            kpi = dict(zip(cols, row)) if row else {}
            result["executive_kpi"] = kpi
            logger.info("Executive KPI sample: %s", kpi)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SupplySight AI analytics layer")
    parser.add_argument("--views-only", action="store_true")
    parser.add_argument("--matviews-only", action="store_true")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Only refresh existing materialized views",
    )
    parser.add_argument("--skip-verify", action="store_true")
    args = parser.parse_args()

    setup_module_logging()
    logger.info("Analytics build starting")

    try:
        if args.refresh:
            refresh_matviews()
            if not args.skip_verify:
                verify()
            logger.info("Materialized view refresh completed")
            return 0

        if not args.matviews_only:
            apply_views()
        if not args.views_only:
            apply_matviews()

        if not args.skip_verify:
            result = verify()
            missing = [
                n
                for n in (*ANALYTICS_VIEWS, *ANALYTICS_MATVIEWS)
                if (
                    (n in ANALYTICS_VIEWS and result["views"].get(n) is None)  # type: ignore[index]
                    or (n in ANALYTICS_MATVIEWS and result["matviews"].get(n) is None)  # type: ignore[index]
                )
            ]
            if missing:
                logger.error("Missing analytics objects: %s", missing)
                return 1

        logger.info("Analytics build completed successfully")
        return 0
    except Exception:
        logger.exception("Analytics build failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
