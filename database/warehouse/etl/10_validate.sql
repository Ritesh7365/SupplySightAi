-- =============================================================================
-- Warehouse ETL validation checks (read-only against public + warehouse)
-- Run after load; returns diagnostic result sets.
-- =============================================================================

-- 1) Row counts: dimensions
SELECT 'dim_date' AS table_name, COUNT(*) AS row_count FROM warehouse.dim_date
UNION ALL SELECT 'dim_department', COUNT(*) FROM warehouse.dim_department
UNION ALL SELECT 'dim_category', COUNT(*) FROM warehouse.dim_category
UNION ALL SELECT 'dim_product', COUNT(*) FROM warehouse.dim_product
UNION ALL SELECT 'dim_customer', COUNT(*) FROM warehouse.dim_customer
UNION ALL SELECT 'dim_location', COUNT(*) FROM warehouse.dim_location
UNION ALL SELECT 'dim_shipping', COUNT(*) FROM warehouse.dim_shipping
UNION ALL SELECT 'fact_sales', COUNT(*) FROM warehouse.fact_sales
UNION ALL SELECT 'fact_shipments', COUNT(*) FROM warehouse.fact_shipments
ORDER BY 1;

-- 2) Source vs warehouse grain reconciliation
SELECT
    (SELECT COUNT(*) FROM public.order_items) AS public_order_items,
    (SELECT COUNT(*) FROM warehouse.fact_sales) AS warehouse_fact_sales,
    (SELECT COUNT(*) FROM public.shipments) AS public_shipments,
    (SELECT COUNT(*) FROM warehouse.fact_shipments) AS warehouse_fact_shipments,
    (SELECT COUNT(*) FROM public.customers) AS public_customers,
    (SELECT COUNT(*) FROM warehouse.dim_customer) AS warehouse_dim_customer,
    (SELECT COUNT(*) FROM public.products) AS public_products,
    (SELECT COUNT(*) FROM warehouse.dim_product) AS warehouse_dim_product;

-- 3) Orphan checks (should all be 0)
SELECT 'fact_sales_orphan_date' AS check_name, COUNT(*) AS orphan_count
FROM warehouse.fact_sales f
LEFT JOIN warehouse.dim_date d ON d.date_key = f.date_key
WHERE d.date_key IS NULL
UNION ALL
SELECT 'fact_sales_orphan_customer', COUNT(*)
FROM warehouse.fact_sales f
LEFT JOIN warehouse.dim_customer d ON d.customer_key = f.customer_key
WHERE d.customer_key IS NULL
UNION ALL
SELECT 'fact_sales_orphan_product', COUNT(*)
FROM warehouse.fact_sales f
LEFT JOIN warehouse.dim_product d ON d.product_key = f.product_key
WHERE d.product_key IS NULL
UNION ALL
SELECT 'fact_shipments_orphan_shipping', COUNT(*)
FROM warehouse.fact_shipments f
LEFT JOIN warehouse.dim_shipping d ON d.shipping_key = f.shipping_key
WHERE d.shipping_key IS NULL;
