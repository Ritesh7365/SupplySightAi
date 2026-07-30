-- =============================================================================
-- analytics.mv_monthly_sales
-- Purpose: Pre-aggregated monthly sales for fast trend dashboards.
-- Refresh: REFRESH MATERIALIZED VIEW analytics.mv_monthly_sales;
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS analytics.mv_monthly_sales CASCADE;

CREATE MATERIALIZED VIEW analytics.mv_monthly_sales AS
SELECT
    d.year_number,
    d.month_number,
    d.year_month,
    d.month_name,
    d.quarter_number,
    d.quarter_name,
    ROUND(SUM(fs.sales), 2)                                     AS sales,
    ROUND(SUM(fs.profit), 2)                                    AS profit,
    ROUND(SUM(fs.discount), 2)                                  AS discount,
    SUM(fs.quantity)                                            AS units_sold,
    COUNT(DISTINCT fs.order_id)                                 AS order_count,
    COUNT(DISTINCT fs.customer_key)                             AS customer_count,
    COUNT(*)                                                    AS line_count,
    ROUND(
        SUM(fs.sales) / NULLIF(COUNT(DISTINCT fs.order_id), 0),
        2
    )                                                           AS average_order_value,
    ROUND(
        SUM(fs.profit) / NULLIF(SUM(fs.sales), 0) * 100,
        2
    )                                                           AS profit_margin_pct
FROM warehouse.fact_sales fs
INNER JOIN warehouse.dim_date d
    ON d.date_key = fs.date_key
GROUP BY
    d.year_number,
    d.month_number,
    d.year_month,
    d.month_name,
    d.quarter_number,
    d.quarter_name
WITH DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_monthly_sales IS
    'Monthly sales/profit aggregates from warehouse.fact_sales. Refresh after warehouse ETL.';

CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_monthly_sales_ym
    ON analytics.mv_monthly_sales (year_month);

CREATE INDEX IF NOT EXISTS ix_mv_monthly_sales_year
    ON analytics.mv_monthly_sales (year_number, month_number);
