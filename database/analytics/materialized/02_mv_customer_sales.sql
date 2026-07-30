-- =============================================================================
-- analytics.mv_customer_sales
-- Purpose: Pre-aggregated customer revenue for ranking and segment dashboards.
-- Refresh: REFRESH MATERIALIZED VIEW analytics.mv_customer_sales;
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS analytics.mv_customer_sales CASCADE;

CREATE MATERIALIZED VIEW analytics.mv_customer_sales AS
SELECT
    c.customer_key,
    c.customer_id,
    TRIM(CONCAT(COALESCE(c.first_name, ''), ' ', COALESCE(c.last_name, ''))) AS customer_name,
    c.customer_segment,
    c.city                                                      AS customer_city,
    c.country                                                   AS customer_country,
    ROUND(SUM(fs.sales), 2)                                     AS sales,
    ROUND(SUM(fs.profit), 2)                                    AS profit,
    ROUND(SUM(fs.discount), 2)                                  AS discount,
    COUNT(DISTINCT fs.order_id)                                 AS order_count,
    SUM(fs.quantity)                                            AS units_purchased,
    ROUND(
        SUM(fs.sales) / NULLIF(COUNT(DISTINCT fs.order_id), 0),
        2
    )                                                           AS average_order_value,
    ROUND(
        SUM(fs.profit) / NULLIF(SUM(fs.sales), 0) * 100,
        2
    )                                                           AS profit_margin_pct
FROM warehouse.fact_sales fs
INNER JOIN warehouse.dim_customer c
    ON c.customer_key = fs.customer_key
GROUP BY
    c.customer_key,
    c.customer_id,
    c.first_name,
    c.last_name,
    c.customer_segment,
    c.city,
    c.country
WITH DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_customer_sales IS
    'Customer-level sales aggregates from warehouse. Refresh after warehouse ETL.';

CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_customer_sales_key
    ON analytics.mv_customer_sales (customer_key);

CREATE INDEX IF NOT EXISTS ix_mv_customer_sales_segment
    ON analytics.mv_customer_sales (customer_segment);

CREATE INDEX IF NOT EXISTS ix_mv_customer_sales_amount
    ON analytics.mv_customer_sales (sales DESC);
