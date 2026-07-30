-- =============================================================================
-- analytics.vw_sales_performance
-- Purpose: Sales trends by time and geography for reporting dashboards.
-- Supports: Sales by Month / Year / Region / Market (slice in BI).
-- Grain: year × month × market × region.
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_sales_performance AS
SELECT
    d.year_number,
    d.month_number,
    d.year_month,
    d.month_name,
    d.quarter_number,
    d.quarter_name,
    loc.market,
    loc.order_region                                            AS region,
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
INNER JOIN warehouse.dim_location loc
    ON loc.location_key = fs.location_key
GROUP BY
    d.year_number,
    d.month_number,
    d.year_month,
    d.month_name,
    d.quarter_number,
    d.quarter_name,
    loc.market,
    loc.order_region;

COMMENT ON VIEW analytics.vw_sales_performance IS
    'Sales performance by year/month/market/region. Aggregate further in BI for month-only or year-only charts.';
