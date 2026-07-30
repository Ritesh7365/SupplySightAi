-- =============================================================================
-- analytics.vw_shipping_performance
-- Purpose: Logistics KPIs by shipping mode for operations dashboards.
-- Supports: Mode mix, delivery delays, late risk, average shipping time.
-- Grain: One row per shipping mode.
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_shipping_performance AS
SELECT
    s.shipping_key,
    s.shipping_mode,
    s.shipping_mode_group,
    COUNT(*)                                                    AS shipment_count,
    COUNT(DISTINCT fsh.customer_key)                            AS customer_count,
    COUNT(DISTINCT fsh.order_id)                                AS order_count,
    ROUND(AVG(fsh.actual_days)::NUMERIC, 2)                     AS avg_shipping_time_days,
    ROUND(AVG(fsh.scheduled_days)::NUMERIC, 2)                  AS avg_scheduled_days,
    ROUND(
        AVG(fsh.actual_days - fsh.scheduled_days)::NUMERIC,
        2
    )                                                           AS avg_delivery_delay_days,
    SUM(CASE WHEN fsh.actual_days > fsh.scheduled_days THEN 1 ELSE 0 END)
                                                                AS delayed_shipment_count,
    ROUND(
        100.0 * SUM(CASE WHEN fsh.actual_days > fsh.scheduled_days THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0),
        2
    )                                                           AS delay_rate_pct,
    SUM(fsh.late_delivery)                                      AS late_delivery_count,
    ROUND(
        100.0 * SUM(fsh.late_delivery) / NULLIF(COUNT(*), 0),
        2
    )                                                           AS late_delivery_risk_pct,
    SUM(CASE WHEN fsh.delivery_status = 'Late delivery' THEN 1 ELSE 0 END)
                                                                AS late_delivery_status_count,
    SUM(CASE WHEN fsh.delivery_status = 'Shipping on time' THEN 1 ELSE 0 END)
                                                                AS on_time_status_count,
    SUM(CASE WHEN fsh.delivery_status = 'Advance shipping' THEN 1 ELSE 0 END)
                                                                AS advance_shipping_count,
    SUM(CASE WHEN fsh.delivery_status = 'Shipping canceled' THEN 1 ELSE 0 END)
                                                                AS canceled_shipment_count
FROM warehouse.fact_shipments fsh
INNER JOIN warehouse.dim_shipping s
    ON s.shipping_key = fsh.shipping_key
GROUP BY
    s.shipping_key,
    s.shipping_mode,
    s.shipping_mode_group;

COMMENT ON VIEW analytics.vw_shipping_performance IS
    'Shipping mode performance: avg transit days, delay vs schedule, late delivery risk %.';
