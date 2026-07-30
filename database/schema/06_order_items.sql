-- =============================================================================
-- SupplySight AI — order_items
-- Purpose: Order line / item fact table (analytic grain of the DataCo extract).
-- Source: One DataCo row ≈ one Order Item Id.
-- =============================================================================

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id           INTEGER         PRIMARY KEY,
    order_id                INTEGER         NOT NULL,
    product_id              INTEGER         NOT NULL,
    quantity                INTEGER         NOT NULL,
    unit_price              NUMERIC(12, 4)  NOT NULL,
    discount_amount         NUMERIC(12, 4)  NOT NULL DEFAULT 0,
    discount_rate           NUMERIC(8, 6)   NOT NULL DEFAULT 0,
    sales                   NUMERIC(12, 4)  NOT NULL,
    order_item_total        NUMERIC(12, 4)  NOT NULL,
    profit_ratio            NUMERIC(12, 6),
    benefit_amount          NUMERIC(12, 4),
    profit_amount           NUMERIC(12, 4),
    sales_per_customer      NUMERIC(14, 4),
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders (order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products (product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT ck_order_items_quantity_pos
        CHECK (quantity > 0),
    CONSTRAINT ck_order_items_unit_price_nonneg
        CHECK (unit_price >= 0)
);

COMMENT ON TABLE order_items IS
    'Order line facts. Primary analytic grain for sales, margin, and basket analysis.';
COMMENT ON COLUMN order_items.product_id IS
    'FK to products; sourced from Order Item Cardprod Id / Product Card Id.';
COMMENT ON COLUMN order_items.unit_price IS
    'DataCo Order Item Product Price (price without discount).';
COMMENT ON COLUMN order_items.benefit_amount IS
    'Mapped from Benefit per order; varies within some Order Ids in source — stored at line grain.';
COMMENT ON COLUMN order_items.profit_amount IS
    'Mapped from Order Profit Per Order; varies within some Order Ids — stored at line grain.';
COMMENT ON COLUMN order_items.sales_per_customer IS
    'Source denormalized metric (Sales per customer); retained for lineage, not a true customer aggregate.';
