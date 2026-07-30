-- =============================================================================
-- SupplySight AI — indexes
-- Purpose: Supporting indexes for FK lookups, BI filters, and common analytics.
-- Apply after all CREATE TABLE scripts (01–10).
-- =============================================================================

-- ----- departments / categories / products -----
CREATE INDEX IF NOT EXISTS ix_categories_department_id
    ON categories (department_id);

CREATE INDEX IF NOT EXISTS ix_products_category_id
    ON products (category_id);

CREATE INDEX IF NOT EXISTS ix_products_status
    ON products (product_status);

CREATE INDEX IF NOT EXISTS ix_products_name
    ON products (product_name);

-- ----- customers -----
CREATE INDEX IF NOT EXISTS ix_customers_segment
    ON customers (customer_segment);

CREATE INDEX IF NOT EXISTS ix_customers_country_city
    ON customers (country, city);

CREATE INDEX IF NOT EXISTS ix_customers_email
    ON customers (email);

-- ----- orders -----
CREATE INDEX IF NOT EXISTS ix_orders_customer_id
    ON orders (customer_id);

CREATE INDEX IF NOT EXISTS ix_orders_order_date
    ON orders (order_date);

CREATE INDEX IF NOT EXISTS ix_orders_status
    ON orders (order_status);

CREATE INDEX IF NOT EXISTS ix_orders_market_region
    ON orders (market, order_region);

CREATE INDEX IF NOT EXISTS ix_orders_geo
    ON orders (order_country, order_state, order_city);

-- ----- order_items -----
CREATE INDEX IF NOT EXISTS ix_order_items_order_id
    ON order_items (order_id);

CREATE INDEX IF NOT EXISTS ix_order_items_product_id
    ON order_items (product_id);

CREATE INDEX IF NOT EXISTS ix_order_items_order_product
    ON order_items (order_id, product_id);

-- ----- shipments -----
CREATE INDEX IF NOT EXISTS ix_shipments_shipping_mode
    ON shipments (shipping_mode);

CREATE INDEX IF NOT EXISTS ix_shipments_delivery_status
    ON shipments (delivery_status);

CREATE INDEX IF NOT EXISTS ix_shipments_late_risk
    ON shipments (late_delivery_risk);

CREATE INDEX IF NOT EXISTS ix_shipments_shipping_date
    ON shipments (shipping_date);

-- ----- placeholder domain tables -----
CREATE INDEX IF NOT EXISTS ix_inventory_product_id
    ON inventory (product_id);

CREATE INDEX IF NOT EXISTS ix_inventory_warehouse_id
    ON inventory (warehouse_id);

CREATE INDEX IF NOT EXISTS ix_vendor_products_product_id
    ON vendor_products (product_id);

CREATE INDEX IF NOT EXISTS ix_vendors_risk_tier
    ON vendors (risk_tier);
