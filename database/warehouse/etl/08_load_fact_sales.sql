-- =============================================================================
-- Load warehouse.fact_sales
-- Grain: one row per public.order_items.order_item_id
-- Joins dimensions on natural keys; enforces RI via surrogate FKs.
-- Prevents duplicates via UNIQUE(order_item_id) + NOT EXISTS guard.
-- =============================================================================

INSERT INTO warehouse.fact_sales (
    date_key,
    customer_key,
    product_key,
    category_key,
    department_key,
    shipping_key,
    location_key,
    order_id,
    order_item_id,
    quantity,
    sales,
    discount,
    profit,
    profit_ratio,
    source_system,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    TO_CHAR(o.order_date::DATE, 'YYYYMMDD')::INTEGER            AS date_key,
    dc.customer_key,
    dp.product_key,
    dcat.category_key,
    dd.department_key,
    dship.shipping_key,
    dloc.location_key,
    oi.order_id,
    oi.order_item_id,
    oi.quantity,
    oi.sales,
    oi.discount_amount                                          AS discount,
    oi.profit_amount                                            AS profit,
    oi.profit_ratio,
    'public',
    NOW(),
    NOW(),
    NOW()
FROM public.order_items oi
INNER JOIN public.orders o
    ON o.order_id = oi.order_id
INNER JOIN public.products p
    ON p.product_id = oi.product_id
INNER JOIN public.categories c
    ON c.category_id = p.category_id
INNER JOIN public.shipments sh
    ON sh.order_id = o.order_id
INNER JOIN warehouse.dim_customer dc
    ON dc.customer_id = o.customer_id
INNER JOIN warehouse.dim_product dp
    ON dp.product_id = oi.product_id
INNER JOIN warehouse.dim_category dcat
    ON dcat.category_id = c.category_id
INNER JOIN warehouse.dim_department dd
    ON dd.department_id = c.department_id
INNER JOIN warehouse.dim_shipping dship
    ON dship.shipping_mode = sh.shipping_mode
INNER JOIN warehouse.dim_location dloc
    ON dloc.location_bk = MD5(
        COALESCE(o.market, '') || '|' ||
        COALESCE(o.order_region, '') || '|' ||
        COALESCE(o.order_country, '') || '|' ||
        COALESCE(o.order_state, '') || '|' ||
        COALESCE(o.order_city, '') || '|' ||
        COALESCE(o.order_zipcode, '')
    )
INNER JOIN warehouse.dim_date ddte
    ON ddte.date_key = TO_CHAR(o.order_date::DATE, 'YYYYMMDD')::INTEGER
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.fact_sales fs
    WHERE fs.order_item_id = oi.order_item_id
);
