-- =============================================================================
-- analytics.vw_geographic_performance
-- Purpose: Geographic sales for map / regional dashboards.
-- Supports: Sales by Country / State / City.
-- Grain: country × state × city (plus market/region attributes).
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_geographic_performance AS
SELECT
    loc.market,
    loc.order_region                                            AS region,
    loc.order_country                                           AS country,
    loc.order_state                                             AS state,
    loc.order_city                                              AS city,
    ROUND(SUM(fs.sales), 2)                                     AS sales,
    ROUND(SUM(fs.profit), 2)                                    AS profit,
    ROUND(SUM(fs.discount), 2)                                  AS discount,
    SUM(fs.quantity)                                            AS units_sold,
    COUNT(DISTINCT fs.order_id)                                 AS order_count,
    COUNT(DISTINCT fs.customer_key)                             AS customer_count,
    ROUND(
        SUM(fs.sales) / NULLIF(COUNT(DISTINCT fs.order_id), 0),
        2
    )                                                           AS average_order_value,
    ROUND(
        SUM(fs.profit) / NULLIF(SUM(fs.sales), 0) * 100,
        2
    )                                                           AS profit_margin_pct,
    RANK() OVER (ORDER BY SUM(fs.sales) DESC)                   AS geo_sales_rank,
    RANK() OVER (
        PARTITION BY loc.order_country
        ORDER BY SUM(fs.sales) DESC
    )                                                           AS country_city_sales_rank
FROM warehouse.fact_sales fs
INNER JOIN warehouse.dim_location loc
    ON loc.location_key = fs.location_key
GROUP BY
    loc.market,
    loc.order_region,
    loc.order_country,
    loc.order_state,
    loc.order_city;

COMMENT ON VIEW analytics.vw_geographic_performance IS
    'Sales by country/state/city. Roll up in BI: GROUP BY country, or filter geo_sales_rank.';
