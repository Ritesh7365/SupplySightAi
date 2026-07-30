-- =============================================================================
-- SupplySight AI — warehouses (PLACEHOLDER)
-- Purpose: Physical / logical warehouse master for future inventory optimization.
-- Status: Schema only. DataCo extract does not provide warehouse master data.
-- Population: Deferred to synthetic or external WMS / ERP feeds.
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id     SERIAL         PRIMARY KEY,
    warehouse_code   VARCHAR(50)    NOT NULL,
    warehouse_name   VARCHAR(150)   NOT NULL,
    city             VARCHAR(100),
    state_code       VARCHAR(50),
    country          VARCHAR(100),
    postal_code      VARCHAR(20),
    latitude         NUMERIC(10, 6),
    longitude        NUMERIC(10, 6),
    is_active        BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_warehouses_code UNIQUE (warehouse_code)
);

COMMENT ON TABLE warehouses IS
    'PLACEHOLDER: Warehouse master. Not populated from DataCoSupplyChainDataset.csv.';
COMMENT ON COLUMN warehouses.warehouse_code IS
    'Stable business code for integrations (WMS/ERP).';
