-- =============================================================================
-- SupplySight AI — warehouse.dim_location
-- Role: Order destination / market geography dimension (deduplicated).
-- Source: Distinct geographic attributes from public.orders.
-- Natural key: location_bk (stable hash of geo attributes).
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_location (
    location_key        BIGSERIAL       NOT NULL,
    location_bk         CHAR(32)        NOT NULL,
    market              VARCHAR(50),
    order_region        VARCHAR(100),
    order_country       VARCHAR(100),
    order_state         VARCHAR(100),
    order_city          VARCHAR(100),
    order_zipcode       VARCHAR(20),
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_dim_location PRIMARY KEY (location_key),
    CONSTRAINT uq_dim_location_nk UNIQUE (location_bk)
);

COMMENT ON TABLE warehouse.dim_location IS
    'Deduplicated order-destination geography. Built from distinct public.orders geo fields.';
COMMENT ON COLUMN warehouse.dim_location.location_key IS
    'Surrogate primary key for warehouse joins.';
COMMENT ON COLUMN warehouse.dim_location.location_bk IS
    'Natural business key: MD5 of market|region|country|state|city|zipcode.';
COMMENT ON COLUMN warehouse.dim_location.order_zipcode IS
    'Often null in source (~86%); retained when present.';
