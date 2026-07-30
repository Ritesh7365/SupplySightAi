-- =============================================================================
-- Load warehouse.dim_product from public.products
-- =============================================================================

INSERT INTO warehouse.dim_product (
    product_id,
    product_name,
    category_id,
    product_price,
    product_status,
    product_status_desc,
    product_image_url,
    source_system,
    source_updated_at,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    p.product_id,
    p.product_name,
    p.category_id,
    p.product_price,
    p.product_status,
    CASE p.product_status
        WHEN 0 THEN 'Available'
        WHEN 1 THEN 'Not Available'
        ELSE 'Unknown'
    END,
    p.product_image_url,
    'public',
    p.updated_at,
    NOW(),
    NOW(),
    NOW()
FROM public.products p
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.dim_product w
    WHERE w.product_id = p.product_id
);
