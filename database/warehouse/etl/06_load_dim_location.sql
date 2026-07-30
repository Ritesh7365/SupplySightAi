-- =============================================================================
-- Load warehouse.dim_location
-- Deduplicated distinct order geography from public.orders.
-- Natural key = MD5(market|region|country|state|city|zipcode).
-- =============================================================================

INSERT INTO warehouse.dim_location (
    location_bk,
    market,
    order_region,
    order_country,
    order_state,
    order_city,
    order_zipcode,
    source_system,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    loc.location_bk,
    loc.market,
    loc.order_region,
    loc.order_country,
    loc.order_state,
    loc.order_city,
    loc.order_zipcode,
    'public',
    NOW(),
    NOW(),
    NOW()
FROM (
    SELECT DISTINCT
        MD5(
            COALESCE(o.market, '') || '|' ||
            COALESCE(o.order_region, '') || '|' ||
            COALESCE(o.order_country, '') || '|' ||
            COALESCE(o.order_state, '') || '|' ||
            COALESCE(o.order_city, '') || '|' ||
            COALESCE(o.order_zipcode, '')
        ) AS location_bk,
        o.market,
        o.order_region,
        o.order_country,
        o.order_state,
        o.order_city,
        o.order_zipcode
    FROM public.orders o
) loc
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.dim_location w
    WHERE w.location_bk = loc.location_bk
);
