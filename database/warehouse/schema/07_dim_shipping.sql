-- =============================================================================
-- SupplySight AI — warehouse.dim_shipping
-- Role: Shipping mode / service-level dimension.
-- Source: Distinct shipping_mode values from public.shipments.
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_shipping (
    shipping_key        BIGSERIAL       NOT NULL,
    shipping_mode       VARCHAR(50)     NOT NULL,
    shipping_mode_group VARCHAR(30)     NOT NULL,
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_dim_shipping PRIMARY KEY (shipping_key),
    CONSTRAINT uq_dim_shipping_nk UNIQUE (shipping_mode)
);

COMMENT ON TABLE warehouse.dim_shipping IS
    'Shipping mode dimension (Standard Class, First Class, Second Class, Same Day, …).';
COMMENT ON COLUMN warehouse.dim_shipping.shipping_key IS
    'Surrogate primary key for warehouse joins.';
COMMENT ON COLUMN warehouse.dim_shipping.shipping_mode IS
    'Natural business key from public.shipments.shipping_mode.';
COMMENT ON COLUMN warehouse.dim_shipping.shipping_mode_group IS
    'Coarse grouping: Express (Same Day/First Class) vs Standard (Second/Standard Class) vs Other.';
