-- =============================================================================
-- SupplySight AI — warehouse.dim_product
-- Role: Product / SKU catalog dimension.
-- Source: public.products.
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    product_key         BIGSERIAL       NOT NULL,
    product_id          INTEGER         NOT NULL,
    product_name        VARCHAR(255)    NOT NULL,
    category_id         INTEGER         NOT NULL,
    product_price       NUMERIC(12, 4)  NOT NULL,
    product_status      SMALLINT        NOT NULL,
    product_status_desc VARCHAR(20)     NOT NULL,
    product_image_url   TEXT,
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    source_updated_at   TIMESTAMPTZ,
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_dim_product PRIMARY KEY (product_key),
    CONSTRAINT uq_dim_product_nk UNIQUE (product_id),
    CONSTRAINT ck_dim_product_status CHECK (product_status IN (0, 1))
);

COMMENT ON TABLE warehouse.dim_product IS
    'Product dimension. One row per Product Card Id from the OLTP catalog.';
COMMENT ON COLUMN warehouse.dim_product.product_key IS
    'Surrogate primary key for warehouse joins.';
COMMENT ON COLUMN warehouse.dim_product.product_id IS
    'Natural business key from public.products.product_id.';
COMMENT ON COLUMN warehouse.dim_product.product_status_desc IS
    'Decoded product_status: 0=Available, 1=Not Available.';
COMMENT ON COLUMN warehouse.dim_product.category_id IS
    'Source category natural key for lineage; fact also carries category_key.';
