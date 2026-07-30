-- =============================================================================
-- SupplySight AI — products
-- Purpose: Product catalog dimension (sellable SKUs / card products).
-- Source: Product Card Id and product attributes; Category Id for taxonomy.
-- =============================================================================

CREATE TABLE IF NOT EXISTS products (
    product_id          INTEGER         PRIMARY KEY,
    product_name        VARCHAR(255)    NOT NULL,
    category_id         INTEGER         NOT NULL,
    product_price       NUMERIC(12, 4)  NOT NULL,
    product_status      SMALLINT        NOT NULL DEFAULT 0,
    product_description TEXT,
    product_image_url   TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT ck_products_status
        CHECK (product_status IN (0, 1)),
    CONSTRAINT ck_products_price_nonneg
        CHECK (product_price >= 0)
);

COMMENT ON TABLE products IS
    'Product catalog. product_id maps to DataCo Product Card Id.';
COMMENT ON COLUMN products.product_status IS
    '0 = available, 1 = not available (DataCo Product Status).';
COMMENT ON COLUMN products.product_description IS
    'Often null in source extract; retained for future enrichment.';
COMMENT ON COLUMN products.product_image_url IS
    'DataCo Product Image link.';
