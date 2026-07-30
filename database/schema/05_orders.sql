-- =============================================================================
-- SupplySight AI — orders
-- Purpose: Order header fact/dimension hybrid (one row per Order Id).
-- Source: Order-level attributes consistent per Order Id in DataCo.
-- Grain: 1 order : N order_items ; 1 order : 1 shipment (in current extract).
-- =============================================================================

CREATE TABLE IF NOT EXISTS orders (
    order_id              INTEGER         PRIMARY KEY,
    customer_id           INTEGER         NOT NULL,
    order_date            TIMESTAMP       NOT NULL,
    order_status          VARCHAR(50)     NOT NULL,
    transaction_type      VARCHAR(50)     NOT NULL,
    market                VARCHAR(50),
    order_city            VARCHAR(100),
    order_state           VARCHAR(100),
    order_country         VARCHAR(100),
    order_region          VARCHAR(100),
    order_zipcode         VARCHAR(20),
    created_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMENT ON TABLE orders IS
    'Order header. Natural key Order Id. Delivery metrics live in shipments.';
COMMENT ON COLUMN orders.customer_id IS
    'FK to customers; sourced from Order Customer Id (= Customer Id in extract).';
COMMENT ON COLUMN orders.transaction_type IS
    'DataCo Type (payment/transaction type).';
COMMENT ON COLUMN orders.order_date IS
    'Parsed from order date (DateOrders).';
COMMENT ON COLUMN orders.order_zipcode IS
    'Often missing in source (~86% null); nullable by design.';
