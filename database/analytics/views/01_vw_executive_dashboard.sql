-- =============================================================================
-- analytics.vw_executive_dashboard
-- Purpose: Single-row KPI snapshot for executive / C-level dashboards.
-- Source: warehouse.fact_sales + warehouse.fact_shipments (read-only).
-- Grain: One row (enterprise totals).
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_executive_dashboard AS
SELECT
    ROUND(COALESCE(s.total_sales, 0), 2)                         AS total_sales,
    ROUND(COALESCE(s.total_profit, 0), 2)                        AS total_profit,
    COALESCE(s.total_orders, 0)                                  AS total_orders,
    COALESCE(s.total_customers, 0)                               AS total_customers,
    ROUND(
        COALESCE(s.total_sales, 0) / NULLIF(s.total_orders, 0),
        2
    )                                                            AS average_order_value,
    ROUND(
        100.0 * COALESCE(sh.late_shipments, 0)
            / NULLIF(sh.total_shipments, 0),
        2
    )                                                            AS late_delivery_pct,
    COALESCE(sh.total_shipments, 0)                              AS total_shipments,
    COALESCE(sh.late_shipments, 0)                               AS late_shipments,
    ROUND(
        COALESCE(s.total_profit, 0) / NULLIF(s.total_sales, 0) * 100,
        2
    )                                                            AS overall_profit_margin_pct,
    NOW()                                                        AS refreshed_at
FROM (
    SELECT
        SUM(fs.sales)                       AS total_sales,
        SUM(fs.profit)                      AS total_profit,
        COUNT(DISTINCT fs.order_id)         AS total_orders,
        COUNT(DISTINCT fs.customer_key)     AS total_customers
    FROM warehouse.fact_sales fs
) s
CROSS JOIN (
    SELECT
        COUNT(*)                            AS total_shipments,
        SUM(fsh.late_delivery)              AS late_shipments
    FROM warehouse.fact_shipments fsh
) sh;

COMMENT ON VIEW analytics.vw_executive_dashboard IS
    'Executive KPI dashboard: sales, profit, orders, customers, AOV, late delivery %. Grain: 1 row.';
