-- =============================================================================
-- SupplySight AI — departments
-- Purpose: Store / merchandising department dimension.
-- Source: Department Id, Department Name (deduplicated from DataCo).
-- =============================================================================

CREATE TABLE IF NOT EXISTS departments (
    department_id   INTEGER       PRIMARY KEY,
    department_name VARCHAR(100)  NOT NULL,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_departments_name UNIQUE (department_name)
);

COMMENT ON TABLE departments IS
    'Merchandising/store departments. One department owns many categories.';
COMMENT ON COLUMN departments.department_id IS
    'Natural key from DataCo Department Id.';
COMMENT ON COLUMN departments.department_name IS
    'Human-readable department label from DataCo Department Name.';
