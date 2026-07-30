-- =============================================================================
-- Load warehouse.fact_shipments
-- Grain: one row per public.shipments.shipment_id (1:1 with orders in source).
-- date_key uses order_date for alignment with fact_sales time analysis.
-- =============================================================================

INSERT INTO warehouse.fact_shipments (
    shipping_key,
    customer_key,
    date_key,
    order_id,
    source_shipment_id,
    actual_days,
    scheduled_days,
    late_delivery,
    delivery_status,
    source_system,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    dship.shipping_key,
    dc.customer_key,
    TO_CHAR(o.order_date::DATE, 'YYYYMMDD')::INTEGER            AS date_key,
    sh.order_id,
    sh.shipment_id                                              AS source_shipment_id,
    sh.days_for_shipping_real                                   AS actual_days,
    sh.days_for_shipment_scheduled                              AS scheduled_days,
    sh.late_delivery_risk                                       AS late_delivery,
    sh.delivery_status,
    'public',
    NOW(),
    NOW(),
    NOW()
FROM public.shipments sh
INNER JOIN public.orders o
    ON o.order_id = sh.order_id
INNER JOIN warehouse.dim_shipping dship
    ON dship.shipping_mode = sh.shipping_mode
INNER JOIN warehouse.dim_customer dc
    ON dc.customer_id = o.customer_id
INNER JOIN warehouse.dim_date ddte
    ON ddte.date_key = TO_CHAR(o.order_date::DATE, 'YYYYMMDD')::INTEGER
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.fact_shipments fs
    WHERE fs.source_shipment_id = sh.shipment_id
);
