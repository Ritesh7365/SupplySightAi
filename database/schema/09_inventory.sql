-- =============================================================================
-- SupplySight AI — inventory (PLACEHOLDER)
-- Purpose: On-hand / available inventory balances by product and warehouse.
-- Status: Schema only. DataCo Product Status is a binary availability flag on
--         products, not true inventory quantity by location.
-- Population: Deferred to synthetic or external inventory snapshots.
-- =============================================================================

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id       BIGSERIAL       PRIMARY KEY,
    warehouse_id       INTEGER         NOT NULL,
    product_id         INTEGER         NOT NULL,
    quantity_on_hand   NUMERIC(14, 3)  NOT NULL DEFAULT 0,
    quantity_reserved  NUMERIC(14, 3)  NOT NULL DEFAULT 0,
    quantity_available NUMERIC(14, 3)  GENERATED ALWAYS AS
        (quantity_on_hand - quantity_reserved) STORED,
    reorder_point      NUMERIC(14, 3),
    reorder_quantity   NUMERIC(14, 3),
    as_of_ts           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_inventory_warehouse_product UNIQUE (warehouse_id, product_id),
    CONSTRAINT fk_inventory_warehouse
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id) REFERENCES products (product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT ck_inventory_qty_on_hand
        CHECK (quantity_on_hand >= 0),
    CONSTRAINT ck_inventory_qty_reserved
        CHECK (quantity_reserved >= 0)
);

COMMENT ON TABLE inventory IS
    'PLACEHOLDER: Inventory balances. Not populated from DataCo order extract.';
COMMENT ON COLUMN inventory.quantity_available IS
    'Generated column: on_hand - reserved.';
