-- =============================================================================
-- SupplySight AI — Warehouse supporting indexes
-- Purpose: Join and filter performance for star-schema queries.
-- =============================================================================

-- Dimension natural-key lookups (ETL upsert / join helpers)
CREATE INDEX IF NOT EXISTS ix_dim_department_name
    ON warehouse.dim_department (department_name);

CREATE INDEX IF NOT EXISTS ix_dim_category_name
    ON warehouse.dim_category (category_name);

CREATE INDEX IF NOT EXISTS ix_dim_product_name
    ON warehouse.dim_product (product_name);

CREATE INDEX IF NOT EXISTS ix_dim_customer_segment
    ON warehouse.dim_customer (customer_segment);

CREATE INDEX IF NOT EXISTS ix_dim_location_geo
    ON warehouse.dim_location (market, order_region, order_country);

CREATE INDEX IF NOT EXISTS ix_dim_date_ym
    ON warehouse.dim_date (year_number, month_number);

-- Fact_sales foreign-key and common slice indexes
CREATE INDEX IF NOT EXISTS ix_fact_sales_date
    ON warehouse.fact_sales (date_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_customer
    ON warehouse.fact_sales (customer_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_product
    ON warehouse.fact_sales (product_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_category
    ON warehouse.fact_sales (category_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_department
    ON warehouse.fact_sales (department_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_shipping
    ON warehouse.fact_sales (shipping_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_location
    ON warehouse.fact_sales (location_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_order
    ON warehouse.fact_sales (order_id);

-- Fact_shipments indexes
CREATE INDEX IF NOT EXISTS ix_fact_shipments_date
    ON warehouse.fact_shipments (date_key);
CREATE INDEX IF NOT EXISTS ix_fact_shipments_customer
    ON warehouse.fact_shipments (customer_key);
CREATE INDEX IF NOT EXISTS ix_fact_shipments_shipping
    ON warehouse.fact_shipments (shipping_key);
CREATE INDEX IF NOT EXISTS ix_fact_shipments_late
    ON warehouse.fact_shipments (late_delivery);
