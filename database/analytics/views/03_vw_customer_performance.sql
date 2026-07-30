-- =============================================================================
-- analytics.vw_customer_performance
-- Purpose: Customer revenue, AOV, segment, and ranking for CRM / sales BI.
-- Supports: Top customers, revenue per customer, AOV, segments.
-- Grain: One row per customer.
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_customer_performance AS
SELECT
    c.customer_key,
    c.customer_id,
    TRIM(CONCAT(COALESCE(c.first_name, ''), ' ', COALESCE(c.last_name, ''))) AS customer_name,
    c.customer_segment,
    c.city                                                      AS customer_city,
    c.state_code                                               AS customer_state,
    c.country                                                   AS customer_country,
    ROUND(SUM(fs.sales), 2)                                     AS revenue,
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
    )                                                           AS profit_margin_pct,
    RANK() OVER (ORDER BY SUM(fs.sales) DESC)                   AS revenue_rank,
    DENSE_RANK() OVER (
        PARTITION BY c.customer_segment
        ORDER BY SUM(fs.sales) DESC
    )                                                           AS segment_revenue_rank
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
    c.state_code,
    c.country;

COMMENT ON VIEW analytics.vw_customer_performance IS
    'Per-customer revenue, AOV, segment, and ranks. Filter revenue_rank <= N for top customers.';
