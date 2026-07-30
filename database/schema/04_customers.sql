-- =============================================================================
-- SupplySight AI — customers
-- Purpose: Customer master / bill-to party dimension.
-- Source: Customer Id and customer demographic / address attributes.
-- Note: Email/password are PII — restrict access in production (RLS / views).
-- =============================================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id       INTEGER         PRIMARY KEY,
    first_name        VARCHAR(100)    NOT NULL,
    last_name         VARCHAR(100),
    email             VARCHAR(255),
    password_mask     VARCHAR(255),
    customer_segment  VARCHAR(50)     NOT NULL,
    street            VARCHAR(255),
    city              VARCHAR(100),
    state_code        VARCHAR(50),
    zipcode           VARCHAR(20),
    country           VARCHAR(100),
    latitude          NUMERIC(10, 6),
    longitude         NUMERIC(10, 6),
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_customers_segment
        CHECK (customer_segment IN ('Consumer', 'Corporate', 'Home Office'))
);

COMMENT ON TABLE customers IS
    'Customer dimension. customer_id maps to DataCo Customer Id.';
COMMENT ON COLUMN customers.password_mask IS
    'Masked customer key from source — treat as sensitive credential material.';
COMMENT ON COLUMN customers.latitude IS
    'Geo coordinate associated with customer/store registration in DataCo.';
COMMENT ON COLUMN customers.longitude IS
    'Geo coordinate associated with customer/store registration in DataCo.';
