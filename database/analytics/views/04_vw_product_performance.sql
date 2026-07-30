-- =============================================================================
-- analytics.vw_product_performance
-- Purpose: Product and category sales / profit for merchandising dashboards.
-- Supports: Best / lowest selling products, profit by product, category perf.
-- Grain: One row per product (with category & department attributes).
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_product_performance AS
SELECT
    p.product_key,
    p.product_id,
    p.product_name,
    p.product_price,
    p.product_status_desc,
    cat.category_key,
    cat.category_id,
    cat.category_name,
    dep.department_key,
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
    )                                                           AS profit_margin_pct,
    RANK() OVER (ORDER BY SUM(fs.sales) DESC)                   AS best_selling_rank,
    RANK() OVER (ORDER BY SUM(fs.sales) ASC)                    AS lowest_selling_rank,
    RANK() OVER (ORDER BY SUM(fs.profit) DESC)                  AS profit_rank,
    RANK() OVER (
        PARTITION BY cat.category_id
        ORDER BY SUM(fs.sales) DESC
    )                                                           AS category_sales_rank,
    ROUND(SUM(SUM(fs.sales)) OVER (PARTITION BY cat.category_id), 2) AS category_total_sales,
    ROUND(SUM(SUM(fs.profit)) OVER (PARTITION BY cat.category_id), 2) AS category_total_profit
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
    p.product_status_desc,
    cat.category_key,
    cat.category_id,
    cat.category_name,
    dep.department_key,
    dep.department_id,
    dep.department_name;

COMMENT ON VIEW analytics.vw_product_performance IS
    'Product sales/profit with best/lowest ranks and category rollups. Filter best_selling_rank or lowest_selling_rank.';
