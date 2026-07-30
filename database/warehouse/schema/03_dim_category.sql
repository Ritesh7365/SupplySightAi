-- =============================================================================
-- SupplySight AI — warehouse.dim_category
-- Role: Product category dimension (star leaf; department joined via facts).
-- Source: public.categories.
-- Note: category_name is NOT unique in source (e.g. Electronics ×2).
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_category (
    category_key        BIGSERIAL       NOT NULL,
    category_id         INTEGER         NOT NULL,
    category_name       VARCHAR(120)    NOT NULL,
    department_id       INTEGER         NOT NULL,
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    source_updated_at   TIMESTAMPTZ,
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_dim_category PRIMARY KEY (category_key),
    CONSTRAINT uq_dim_category_nk UNIQUE (category_id)
);

COMMENT ON TABLE warehouse.dim_category IS
    'Category dimension. Natural key category_id; department_id retained for lineage.';
COMMENT ON COLUMN warehouse.dim_category.category_key IS
    'Surrogate primary key for warehouse joins.';
COMMENT ON COLUMN warehouse.dim_category.category_id IS
    'Natural business key from public.categories.category_id.';
COMMENT ON COLUMN warehouse.dim_category.department_id IS
    'Source department natural key (lineage); fact also carries department_key.';
