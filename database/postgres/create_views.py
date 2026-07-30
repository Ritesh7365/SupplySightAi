"""
SupplySight AI — Analytics views on public tables.

Creates reusable SQL views in the ``analytics`` schema for BI / reporting.
Safe to re-run (CREATE OR REPLACE VIEW).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import execute_sql_script, get_connection, setup_module_logging  # noqa: E402

logger = logging.getLogger("supplysight.postgres.views")

ANALYTICS_VIEWS_SQL = """
-- ---------------------------------------------------------------------------
-- Order-line analytic grain (joins dimensions + shipment)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.v_order_line_facts AS
SELECT
    oi.order_item_id,
    oi.order_id,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    oi.discount_amount,
    oi.discount_rate,
    oi.sales,
    oi.order_item_total,
    oi.profit_ratio,
    oi.benefit_amount,
    oi.profit_amount,
    o.order_date,
    o.order_status,
    o.transaction_type,
    o.market,
    o.order_region,
    o.order_country,
    o.order_state,
    o.order_city,
    o.customer_id,
    c.customer_segment,
    c.country AS customer_country,
    p.product_name,
    p.category_id,
    cat.category_name,
    cat.department_id,
    d.department_name,
    s.shipping_mode,
    s.delivery_status,
    s.late_delivery_risk,
    s.days_for_shipping_real,
    s.days_for_shipment_scheduled,
    s.shipping_date
FROM public.order_items AS oi
JOIN public.orders AS o
  ON o.order_id = oi.order_id
JOIN public.customers AS c
  ON c.customer_id = o.customer_id
JOIN public.products AS p
  ON p.product_id = oi.product_id
JOIN public.categories AS cat
  ON cat.category_id = p.category_id
JOIN public.departments AS d
  ON d.department_id = cat.department_id
LEFT JOIN public.shipments AS s
  ON s.order_id = o.order_id;

COMMENT ON VIEW analytics.v_order_line_facts IS
    'Denormalized order-line fact view for BI; source of truth remains public tables.';

-- ---------------------------------------------------------------------------
-- Delivery / SLA oriented view (order grain)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.v_delivery_performance AS
SELECT
    o.order_id,
    o.order_date,
    o.order_status,
    o.market,
    o.order_region,
    o.order_country,
    s.shipping_mode,
    s.delivery_status,
    s.late_delivery_risk,
    s.days_for_shipping_real,
    s.days_for_shipment_scheduled,
    (s.days_for_shipping_real - s.days_for_shipment_scheduled) AS shipping_day_variance,
    s.shipping_date
FROM public.orders AS o
LEFT JOIN public.shipments AS s
  ON s.order_id = o.order_id;

COMMENT ON VIEW analytics.v_delivery_performance IS
    'Order-level delivery performance attributes for SLA monitoring.';

-- ---------------------------------------------------------------------------
-- Product catalog view
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.v_product_catalog AS
SELECT
    p.product_id,
    p.product_name,
    p.product_price,
    p.product_status,
    p.category_id,
    c.category_name,
    c.department_id,
    d.department_name
FROM public.products AS p
JOIN public.categories AS c
  ON c.category_id = p.category_id
JOIN public.departments AS d
  ON d.department_id = c.department_id;

COMMENT ON VIEW analytics.v_product_catalog IS
    'Product catalog with category and department labels.';
"""


def create_analytics_views() -> None:
    """Create or replace analytics views."""
    with get_connection(autocommit=False) as conn:
        execute_sql_script(ANALYTICS_VIEWS_SQL, conn=conn)
        conn.commit()
    logger.info("Analytics views created/updated in schema analytics")


def main() -> int:
    """CLI entrypoint."""
    setup_module_logging()
    try:
        create_analytics_views()
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to create views: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
