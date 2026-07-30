-- =============================================================================
-- SupplySight AI — vendors (PLACEHOLDER)
-- Purpose: Supplier / vendor master for procurement and vendor-risk analytics.
-- Status: Schema only. DataCo extract has no vendor identifiers.
-- Population: Deferred to synthetic or external procurement / SRM datasets.
-- =============================================================================

CREATE TABLE IF NOT EXISTS vendors (
    vendor_id        SERIAL         PRIMARY KEY,
    vendor_code      VARCHAR(50)    NOT NULL,
    vendor_name      VARCHAR(200)   NOT NULL,
    contact_email    VARCHAR(255),
    contact_phone    VARCHAR(50),
    country          VARCHAR(100),
    city             VARCHAR(100),
    risk_tier        VARCHAR(30),
    is_active        BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_vendors_code UNIQUE (vendor_code),
    CONSTRAINT ck_vendors_risk_tier
        CHECK (
            risk_tier IS NULL
            OR risk_tier IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
        )
);

-- Optional future bridge: which vendors supply which products
CREATE TABLE IF NOT EXISTS vendor_products (
    vendor_product_id  BIGSERIAL     PRIMARY KEY,
    vendor_id          INTEGER       NOT NULL,
    product_id         INTEGER       NOT NULL,
    vendor_sku         VARCHAR(100),
    lead_time_days     INTEGER,
    unit_cost          NUMERIC(12, 4),
    is_preferred       BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_vendor_products UNIQUE (vendor_id, product_id),
    CONSTRAINT fk_vendor_products_vendor
        FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_vendor_products_product
        FOREIGN KEY (product_id) REFERENCES products (product_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT ck_vendor_products_lead_time
        CHECK (lead_time_days IS NULL OR lead_time_days >= 0)
);

COMMENT ON TABLE vendors IS
    'PLACEHOLDER: Vendor master. Not populated from DataCoSupplyChainDataset.csv.';
COMMENT ON TABLE vendor_products IS
    'PLACEHOLDER: Vendor–product supply relationship for future procurement analytics.';
