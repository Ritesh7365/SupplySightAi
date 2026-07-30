-- =============================================================================
-- SupplySight AI — warehouse.fact_shipments
-- Role: Shipment / delivery performance fact (one row per order shipment).
-- Source: public.shipments ⊕ orders.
-- Measures: actual_days, scheduled_days, late_delivery.
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.fact_shipments (
    shipment_key        BIGSERIAL       NOT NULL,
    -- Dimension FKs
    shipping_key        BIGINT          NOT NULL,
    customer_key        BIGINT          NOT NULL,
    date_key            INTEGER         NOT NULL,
    -- Degenerate / lineage
    order_id            INTEGER         NOT NULL,
    source_shipment_id  BIGINT          NOT NULL,
    -- Measures
    actual_days         INTEGER,
    scheduled_days      INTEGER,
    late_delivery       SMALLINT        NOT NULL,
    delivery_status     VARCHAR(50)     NOT NULL,
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_fact_shipments PRIMARY KEY (shipment_key),
    CONSTRAINT uq_fact_shipments_source UNIQUE (source_shipment_id),
    CONSTRAINT uq_fact_shipments_order UNIQUE (order_id),
    CONSTRAINT fk_fact_shipments_shipping
        FOREIGN KEY (shipping_key) REFERENCES warehouse.dim_shipping (shipping_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_shipments_customer
        FOREIGN KEY (customer_key) REFERENCES warehouse.dim_customer (customer_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_shipments_date
        FOREIGN KEY (date_key) REFERENCES warehouse.dim_date (date_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_fact_shipments_late
        CHECK (late_delivery IN (0, 1)),
    CONSTRAINT ck_fact_shipments_actual_nonneg
        CHECK (actual_days IS NULL OR actual_days >= 0),
    CONSTRAINT ck_fact_shipments_sched_nonneg
        CHECK (scheduled_days IS NULL OR scheduled_days >= 0)
);

COMMENT ON TABLE warehouse.fact_shipments IS
    'Shipment fact — grain = one shipment per order. Delivery performance metrics.';
COMMENT ON COLUMN warehouse.fact_shipments.shipment_key IS
    'Surrogate primary key for the shipment fact row.';
COMMENT ON COLUMN warehouse.fact_shipments.source_shipment_id IS
    'Natural lineage key from public.shipments.shipment_id; prevents duplicate loads.';
COMMENT ON COLUMN warehouse.fact_shipments.date_key IS
    'Order date (from public.orders.order_date) for consistent time analysis with sales.';
COMMENT ON COLUMN warehouse.fact_shipments.actual_days IS
    'Days for shipping (real) from public.shipments.days_for_shipping_real.';
COMMENT ON COLUMN warehouse.fact_shipments.scheduled_days IS
    'Scheduled shipment days from public.shipments.days_for_shipment_scheduled.';
COMMENT ON COLUMN warehouse.fact_shipments.late_delivery IS
    '1 = late delivery risk / late, 0 = on time (from late_delivery_risk).';
COMMENT ON COLUMN warehouse.fact_shipments.delivery_status IS
    'Source delivery status label retained for analysis (not a separate dimension).';
