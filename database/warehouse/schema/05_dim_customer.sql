-- =============================================================================
-- SupplySight AI — warehouse.dim_customer
-- Role: Customer / bill-to party dimension.
-- Source: public.customers.
-- PII: password_mask intentionally excluded from the warehouse.
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key        BIGSERIAL       NOT NULL,
    customer_id         INTEGER         NOT NULL,
    first_name          VARCHAR(100)    NOT NULL,
    last_name           VARCHAR(100),
    email               VARCHAR(255),
    customer_segment    VARCHAR(50)     NOT NULL,
    street              VARCHAR(255),
    city                VARCHAR(100),
    state_code          VARCHAR(50),
    zipcode             VARCHAR(20),
    country             VARCHAR(100),
    latitude            NUMERIC(10, 6),
    longitude           NUMERIC(10, 6),
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    source_updated_at   TIMESTAMPTZ,
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key),
    CONSTRAINT uq_dim_customer_nk UNIQUE (customer_id)
);

COMMENT ON TABLE warehouse.dim_customer IS
    'Customer dimension for sales and shipment analysis. Excludes credential fields.';
COMMENT ON COLUMN warehouse.dim_customer.customer_key IS
    'Surrogate primary key for warehouse joins.';
COMMENT ON COLUMN warehouse.dim_customer.customer_id IS
    'Natural business key from public.customers.customer_id (DataCo Customer Id).';
COMMENT ON COLUMN warehouse.dim_customer.email IS
    'PII — restrict access in production (views / RLS).';
