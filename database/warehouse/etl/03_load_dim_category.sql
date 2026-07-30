-- =============================================================================
-- Load warehouse.dim_category from public.categories
-- =============================================================================

INSERT INTO warehouse.dim_category (
    category_id,
    category_name,
    department_id,
    source_system,
    source_updated_at,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    c.category_id,
    c.category_name,
    c.department_id,
    'public',
    c.updated_at,
    NOW(),
    NOW(),
    NOW()
FROM public.categories c
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.dim_category w
    WHERE w.category_id = c.category_id
);
