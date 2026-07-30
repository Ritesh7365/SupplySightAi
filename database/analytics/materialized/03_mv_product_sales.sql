-- =============================================================================
-- analytics.mv_product_sales
-- Purpose: Pre-aggregated product sales for merchandising dashboards.
-- Refresh: REFRESH MATERIALIZED VIEW analytics.mv_product_sales;
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS analytics.mv_product_sales CASCADE;

CREATE MATERIALIZED VIEW analytics.mv_product_sales AS
SELECT
    p.product_key,
    p.product_id,
    p.product_name,
    p.product_price,
    cat.category_id,
    cat.category_name,
    dep.department_id,
    dep.department_name,
    ROUND(SUM(fs.sales), 2)                                     AS sales,
    ROUND(SUM(fs.profit), 2)                                    AS profit,
    ROUND(SUM(fs.discount), 2)                                  AS discount,
    SUM(fs.quantity)                                            AS units_sold,
    COUNT(DISTINCT fs.order_id)                                 AS order_count,
    COUNT(DISTINCT fs.customer_key)                             AS customer_count,
    ROUND(
        SUM(fs.profit) / NULLIF(SUM(fs.sales), 0) * 100,
        2
    )                                                           AS profit_margin_pct
FROM warehouse.fact_sales fs
INNER JOIN warehouse.dim_product p
    ON p.product_key = fs.product_key
INNER JOIN warehouse.dim_category cat
    ON cat.category_key = fs.category_key
INNER JOIN warehouse.dim_department dep
    ON dep.department_key = fs.department_key
GROUP BY
    p.product_key,
    p.product_id,
    p.product_name,
    p.product_price,
    cat.category_id,
    cat.category_name,
    dep.department_id,
    dep.department_name
WITH DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_product_sales IS
    'Product-level sales/profit aggregates from warehouse. Refresh after warehouse ETL.';

CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_product_sales_key
    ON analytics.mv_product_sales (product_key);

CREATE INDEX IF NOT EXISTS ix_mv_product_sales_category
    ON analytics.mv_product_sales (category_id);

CREATE INDEX IF NOT EXISTS ix_mv_product_sales_amount
    ON analytics.mv_product_sales (sales DESC);
