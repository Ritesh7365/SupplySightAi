-- =============================================================================
-- Load warehouse.dim_department from public.departments
-- =============================================================================

INSERT INTO warehouse.dim_department (
    department_id,
    department_name,
    source_system,
    source_updated_at,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    d.department_id,
    d.department_name,
    'public',
    d.updated_at,
    NOW(),
    NOW(),
    NOW()
FROM public.departments d
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.dim_department w
    WHERE w.department_id = d.department_id
);
