-- =============================================================================
-- SupplySight AI — warehouse.fact_sales
-- Role: Sales fact at order-line grain (order_item).
-- Source: public.order_items ⊕ orders ⊕ products ⊕ categories ⊕ shipments.
-- Measures: quantity, sales, discount, profit, profit_ratio.
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sales_key           BIGSERIAL       NOT NULL,
    -- Dimension FKs
    date_key            INTEGER         NOT NULL,
    customer_key        BIGINT          NOT NULL,
    product_key         BIGINT          NOT NULL,
    category_key        BIGINT          NOT NULL,
    department_key      BIGINT          NOT NULL,
    shipping_key        BIGINT          NOT NULL,
    location_key        BIGINT          NOT NULL,
    -- Degenerate / business keys
    order_id            INTEGER         NOT NULL,
    order_item_id       INTEGER         NOT NULL,
    -- Measures
    quantity            INTEGER         NOT NULL,
    sales               NUMERIC(12, 4)  NOT NULL,
    discount            NUMERIC(12, 4)  NOT NULL,
    profit              NUMERIC(12, 4),
    profit_ratio        NUMERIC(12, 6),
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_fact_sales PRIMARY KEY (sales_key),
    CONSTRAINT uq_fact_sales_order_item UNIQUE (order_item_id),
    CONSTRAINT fk_fact_sales_date
        FOREIGN KEY (date_key) REFERENCES warehouse.dim_date (date_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_sales_customer
        FOREIGN KEY (customer_key) REFERENCES warehouse.dim_customer (customer_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_sales_product
        FOREIGN KEY (product_key) REFERENCES warehouse.dim_product (product_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_sales_category
        FOREIGN KEY (category_key) REFERENCES warehouse.dim_category (category_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_sales_department
        FOREIGN KEY (department_key) REFERENCES warehouse.dim_department (department_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_sales_shipping
        FOREIGN KEY (shipping_key) REFERENCES warehouse.dim_shipping (shipping_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_fact_sales_location
        FOREIGN KEY (location_key) REFERENCES warehouse.dim_location (location_key)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_fact_sales_quantity_pos CHECK (quantity > 0)
);

COMMENT ON TABLE warehouse.fact_sales IS
    'Sales fact — grain = one order line (order_item_id). Populated from public OLTP only.';
COMMENT ON COLUMN warehouse.fact_sales.sales_key IS
    'Surrogate primary key for the fact row.';
COMMENT ON COLUMN warehouse.fact_sales.order_item_id IS
    'Natural/degenerate key from public.order_items; enforces no duplicate loads.';
COMMENT ON COLUMN warehouse.fact_sales.order_id IS
    'Degenerate dimension — Order Id for drill-through to operational systems.';
COMMENT ON COLUMN warehouse.fact_sales.discount IS
    'Line discount amount from public.order_items.discount_amount.';
COMMENT ON COLUMN warehouse.fact_sales.profit IS
    'Line profit from public.order_items.profit_amount.';
COMMENT ON COLUMN warehouse.fact_sales.profit_ratio IS
    'Line profit ratio from public.order_items.profit_ratio.';
