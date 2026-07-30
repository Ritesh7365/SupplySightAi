"""
SupplySight AI — Materialized views for analytics accelerators.

Creates materialized views in the ``analytics`` schema. Safe to re-run
(DROP IF EXISTS + CREATE). Refresh later via REFRESH MATERIALIZED VIEW.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import execute_sql_script, get_connection, setup_module_logging  # noqa: E402

logger = logging.getLogger("supplysight.postgres.matviews")

MATERIALIZED_VIEWS_SQL = """
-- ---------------------------------------------------------------------------
-- Daily sales / margin aggregates (empty until public tables are loaded)
-- ---------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS analytics.mv_daily_sales CASCADE;
CREATE MATERIALIZED VIEW analytics.mv_daily_sales AS
SELECT
    DATE(o.order_date) AS sales_date,
    o.market,
    o.order_region,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(oi.order_item_id) AS line_count,
    SUM(oi.sales) AS total_sales,
    SUM(oi.order_item_total) AS total_order_item_amount,
    SUM(oi.profit_amount) AS total_profit_amount
FROM public.order_items AS oi
JOIN public.orders AS o
  ON o.order_id = oi.order_id
GROUP BY DATE(o.order_date), o.market, o.order_region
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_daily_sales IS
    'Daily sales aggregates by market/region. Created WITH NO DATA until first refresh after load.';

CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_daily_sales
    ON analytics.mv_daily_sales (sales_date, market, order_region);

-- ---------------------------------------------------------------------------
-- Late delivery rates by shipping mode
-- ---------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS analytics.mv_late_delivery_by_mode CASCADE;
CREATE MATERIALIZED VIEW analytics.mv_late_delivery_by_mode AS
SELECT
    s.shipping_mode,
    COUNT(*) AS shipment_count,
    SUM(CASE WHEN s.late_delivery_risk = 1 THEN 1 ELSE 0 END) AS late_count,
    ROUND(
        100.0 * SUM(CASE WHEN s.late_delivery_risk = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
        2
    ) AS late_rate_pct,
    AVG(s.days_for_shipping_real)::NUMERIC(10, 2) AS avg_real_ship_days,
    AVG(s.days_for_shipment_scheduled)::NUMERIC(10, 2) AS avg_scheduled_ship_days
FROM public.shipments AS s
GROUP BY s.shipping_mode
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_late_delivery_by_mode IS
    'Late-delivery KPIs by shipping mode. Refresh after shipments are loaded.';

CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_late_delivery_by_mode
    ON analytics.mv_late_delivery_by_mode (shipping_mode);
"""


def create_materialized_views() -> None:
    """
    Create analytics materialized views.

    Uses ``WITH NO DATA`` so initialization succeeds on empty public tables.
    Call ``REFRESH MATERIALIZED VIEW`` after CSV loading in a later phase.
    """
    with get_connection(autocommit=False) as conn:
        execute_sql_script(MATERIALIZED_VIEWS_SQL, conn=conn)
        conn.commit()
    logger.info("Materialized views created in schema analytics (WITH NO DATA)")


def refresh_materialized_views() -> None:
    """
    Refresh all analytics materialized views (run after data load).

    Helper reserved for the future CSV-load phase.
    """
    statements = (
        "REFRESH MATERIALIZED VIEW analytics.mv_daily_sales;",
        "REFRESH MATERIALIZED VIEW analytics.mv_late_delivery_by_mode;",
    )
    with get_connection(autocommit=False) as conn:
        with conn.cursor() as cur:
            for stmt in statements:
                logger.info("Running: %s", stmt.strip())
                cur.execute(stmt)
        conn.commit()
    logger.info("Materialized view refresh complete")


def main() -> int:
    """CLI entrypoint — create mat views only (no refresh / no CSV load)."""
    setup_module_logging()
    try:
        create_materialized_views()
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to create materialized views: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
