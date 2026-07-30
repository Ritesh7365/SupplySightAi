-- =============================================================================
-- Load warehouse.dim_customer from public.customers
-- Excludes password_mask (credential material not stored in DW).
-- =============================================================================

INSERT INTO warehouse.dim_customer (
    customer_id,
    first_name,
    last_name,
    email,
    customer_segment,
    street,
    city,
    state_code,
    zipcode,
    country,
    latitude,
    longitude,
    source_system,
    source_updated_at,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.customer_segment,
    c.street,
    c.city,
    c.state_code,
    c.zipcode,
    c.country,
    c.latitude,
    c.longitude,
    'public',
    c.updated_at,
    NOW(),
    NOW(),
    NOW()
FROM public.customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.dim_customer w
    WHERE w.customer_id = c.customer_id
);
