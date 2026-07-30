-- =============================================================================
-- SupplySight AI — warehouse.dim_department
-- Role: Merchandising department dimension.
-- Source: public.departments (no mutation of public).
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_department (
    department_key      BIGSERIAL       NOT NULL,
    department_id       INTEGER         NOT NULL,
    department_name     VARCHAR(100)    NOT NULL,
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    source_updated_at   TIMESTAMPTZ,
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_dim_department PRIMARY KEY (department_key),
    CONSTRAINT uq_dim_department_nk UNIQUE (department_id)
);

COMMENT ON TABLE warehouse.dim_department IS
    'Department dimension. One row per merchandising department.';
COMMENT ON COLUMN warehouse.dim_department.department_key IS
    'Surrogate primary key for warehouse joins.';
COMMENT ON COLUMN warehouse.dim_department.department_id IS
    'Natural business key from public.departments.department_id (DataCo Department Id).';
COMMENT ON COLUMN warehouse.dim_department.etl_loaded_at IS
    'Timestamp when the row was last loaded by warehouse ETL.';
