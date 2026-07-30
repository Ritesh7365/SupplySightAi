-- =============================================================================
-- SupplySight AI — Operations analytics views (inventory / warehouse / vendor)
-- Source: public.warehouses, inventory, vendors, vendor_products, products
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_inventory_performance AS
SELECT
    i.inventory_id,
    i.warehouse_id,
    w.warehouse_code,
    w.warehouse_name,
    i.product_id,
    p.product_name,
    p.product_price,
    i.quantity_on_hand,
    i.quantity_reserved,
    i.quantity_available,
    i.reorder_point,
    i.reorder_quantity,
    i.safety_stock,
    i.maximum_stock,
    ROUND(i.quantity_available * p.product_price, 2) AS inventory_value,
    CASE
        WHEN i.quantity_available <= 0 THEN 'out_of_stock'
        WHEN i.reorder_point IS NOT NULL
             AND i.quantity_available <= i.reorder_point THEN 'low_stock'
        WHEN i.safety_stock IS NOT NULL
             AND i.quantity_available <= i.safety_stock THEN 'below_safety'
        ELSE 'healthy'
    END AS stock_status,
    i.as_of_ts
FROM public.inventory i
INNER JOIN public.products p
    ON p.product_id = i.product_id
LEFT JOIN public.warehouses w
    ON w.warehouse_id = i.warehouse_id;

COMMENT ON VIEW analytics.vw_inventory_performance IS
    'Inventory balances with value proxy and stock-status flags.';


CREATE OR REPLACE VIEW analytics.vw_warehouse_performance AS
SELECT
    w.warehouse_id,
    w.warehouse_code,
    w.warehouse_name,
    w.warehouse_type,
    w.city,
    w.state_code,
    w.country,
    w.latitude,
    w.longitude,
    w.capacity,
    w.is_active,
    COUNT(i.inventory_id)::int AS products_stored,
    COALESCE(SUM(i.quantity_on_hand), 0) AS units_on_hand,
    COALESCE(SUM(i.quantity_available), 0) AS units_available,
    ROUND(COALESCE(SUM(i.quantity_available * p.product_price), 0), 2) AS inventory_value,
    CASE
        WHEN w.capacity IS NULL OR w.capacity = 0 THEN NULL
        ELSE ROUND(
            (COALESCE(SUM(i.quantity_on_hand), 0) / w.capacity) * 100,
            2
        )
    END AS occupancy_pct,
    COALESCE(w.utilization_percent, CASE
        WHEN w.capacity IS NULL OR w.capacity = 0 THEN NULL
        ELSE ROUND(
            (COALESCE(SUM(i.quantity_on_hand), 0) / w.capacity) * 100,
            2
        )
    END) AS utilization_pct,
    (
        SELECT COUNT(DISTINCT o.order_id)::int
        FROM public.orders o
        WHERE o.order_city = w.city
           OR o.order_state = w.state_code
    ) AS orders_handled_proxy
FROM public.warehouses w
LEFT JOIN public.inventory i
    ON i.warehouse_id = w.warehouse_id
LEFT JOIN public.products p
    ON p.product_id = i.product_id
GROUP BY
    w.warehouse_id,
    w.warehouse_code,
    w.warehouse_name,
    w.warehouse_type,
    w.city,
    w.state_code,
    w.country,
    w.latitude,
    w.longitude,
    w.capacity,
    w.is_active,
    w.utilization_percent;

COMMENT ON VIEW analytics.vw_warehouse_performance IS
    'Warehouse capacity, occupancy, inventory value, and city-order proxy.';


CREATE OR REPLACE VIEW analytics.vw_vendor_performance AS
SELECT
    v.vendor_id,
    v.vendor_code,
    v.vendor_name,
    v.country,
    v.city,
    v.risk_tier,
    v.rating,
    v.on_time_delivery_pct,
    v.lead_time_days AS vendor_lead_time_days,
    v.is_active,
    COUNT(vp.vendor_product_id)::int AS product_count,
    ROUND(AVG(vp.lead_time_days)::numeric, 2) AS avg_product_lead_time_days,
    ROUND(AVG(vp.unit_cost)::numeric, 4) AS avg_unit_cost,
    ROUND(SUM(COALESCE(vp.unit_cost, 0) * COALESCE(vp.minimum_order_qty, 1)), 2)
        AS purchase_volume_proxy,
    COUNT(vp.vendor_product_id) FILTER (WHERE vp.is_preferred) ::int AS preferred_links
FROM public.vendors v
LEFT JOIN public.vendor_products vp
    ON vp.vendor_id = v.vendor_id
GROUP BY
    v.vendor_id,
    v.vendor_code,
    v.vendor_name,
    v.country,
    v.city,
    v.risk_tier,
    v.rating,
    v.on_time_delivery_pct,
    v.lead_time_days,
    v.is_active;

COMMENT ON VIEW analytics.vw_vendor_performance IS
    'Vendor SLA, lead time, rating, and purchase-volume proxy.';
