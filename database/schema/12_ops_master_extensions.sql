-- =============================================================================
-- SupplySight AI — Operations master extensions
-- Adds capacity / utilization / vendor SLA / inventory safety fields.
-- Safe to re-run (ADD COLUMN IF NOT EXISTS).
-- =============================================================================

ALTER TABLE public.warehouses
    ADD COLUMN IF NOT EXISTS warehouse_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS capacity NUMERIC(14, 3),
    ADD COLUMN IF NOT EXISTS utilization_percent NUMERIC(6, 2);

ALTER TABLE public.inventory
    ADD COLUMN IF NOT EXISTS safety_stock NUMERIC(14, 3),
    ADD COLUMN IF NOT EXISTS maximum_stock NUMERIC(14, 3);

ALTER TABLE public.vendors
    ADD COLUMN IF NOT EXISTS lead_time_days INTEGER,
    ADD COLUMN IF NOT EXISTS rating NUMERIC(3, 2),
    ADD COLUMN IF NOT EXISTS on_time_delivery_pct NUMERIC(6, 2);

ALTER TABLE public.vendor_products
    ADD COLUMN IF NOT EXISTS minimum_order_qty NUMERIC(14, 3);

COMMENT ON COLUMN public.warehouses.capacity IS
    'Synthetic/WMS capacity in storage units.';
COMMENT ON COLUMN public.warehouses.utilization_percent IS
    'Snapshot utilization % (units_on_hand / capacity).';
COMMENT ON COLUMN public.warehouses.warehouse_type IS
    'Regional hub, distribution center, or store-fulfillment node.';
COMMENT ON COLUMN public.inventory.safety_stock IS
    'Minimum buffer quantity before expedite.';
COMMENT ON COLUMN public.inventory.maximum_stock IS
    'Storage ceiling for the SKU at the warehouse.';
COMMENT ON COLUMN public.vendors.rating IS
    'Supplier score 1.00–5.00.';
COMMENT ON COLUMN public.vendors.on_time_delivery_pct IS
    'Historical on-time delivery percentage.';
COMMENT ON COLUMN public.vendor_products.minimum_order_qty IS
    'Minimum purchase quantity from the vendor for the product.';
