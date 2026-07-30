-- =============================================================================
-- Load warehouse.dim_shipping from distinct public.shipments.shipping_mode
-- =============================================================================

INSERT INTO warehouse.dim_shipping (
    shipping_mode,
    shipping_mode_group,
    source_system,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    s.shipping_mode,
    CASE
        WHEN s.shipping_mode IN ('Same Day', 'First Class') THEN 'Express'
        WHEN s.shipping_mode IN ('Second Class', 'Standard Class') THEN 'Standard'
        ELSE 'Other'
    END AS shipping_mode_group,
    'public',
    NOW(),
    NOW(),
    NOW()
FROM (
    SELECT DISTINCT shipping_mode
    FROM public.shipments
) s
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.dim_shipping w
    WHERE w.shipping_mode = s.shipping_mode
);
