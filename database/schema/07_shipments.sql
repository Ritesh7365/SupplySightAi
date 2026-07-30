-- =============================================================================
-- SupplySight AI — shipments
-- Purpose: Fulfillment / logistics attributes for an order.
-- Source: Shipping Mode, shipping dates, delivery status, late risk, day counts.
-- Cardinality in current extract: 1 shipment row per order (1:1 with orders).
-- =============================================================================

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id                 BIGSERIAL       PRIMARY KEY,
    order_id                    INTEGER         NOT NULL,
    shipping_mode               VARCHAR(50)     NOT NULL,
    shipping_date               TIMESTAMP,
    delivery_status             VARCHAR(50)     NOT NULL,
    late_delivery_risk          SMALLINT        NOT NULL,
    days_for_shipping_real      INTEGER,
    days_for_shipment_scheduled INTEGER,
    created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_shipments_order UNIQUE (order_id),
    CONSTRAINT fk_shipments_order
        FOREIGN KEY (order_id) REFERENCES orders (order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT ck_shipments_late_risk
        CHECK (late_delivery_risk IN (0, 1)),
    CONSTRAINT ck_shipments_days_real_nonneg
        CHECK (days_for_shipping_real IS NULL OR days_for_shipping_real >= 0),
    CONSTRAINT ck_shipments_days_sched_nonneg
        CHECK (days_for_shipment_scheduled IS NULL OR days_for_shipment_scheduled >= 0)
);

COMMENT ON TABLE shipments IS
    'Order shipment / delivery profile. Unique on order_id for current DataCo extract.';
COMMENT ON COLUMN shipments.late_delivery_risk IS
    '1 = late risk, 0 = not late (DataCo Late_delivery_risk).';
COMMENT ON COLUMN shipments.shipping_date IS
    'Parsed from shipping date (DateOrders).';
