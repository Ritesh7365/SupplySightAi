-- =============================================================================
-- Load warehouse.dim_date
-- Builds a continuous calendar covering all order_date and shipping_date values
-- observed in public.orders / public.shipments. No row duplication.
-- =============================================================================

INSERT INTO warehouse.dim_date (
    date_key,
    calendar_date,
    day_of_week,
    day_name,
    day_of_month,
    day_of_year,
    week_of_year,
    month_number,
    month_name,
    quarter_number,
    quarter_name,
    year_number,
    is_weekend,
    is_month_end,
    year_month,
    source_system,
    etl_loaded_at,
    created_at,
    updated_at
)
SELECT
    TO_CHAR(d.dt, 'YYYYMMDD')::INTEGER                          AS date_key,
    d.dt                                                        AS calendar_date,
    EXTRACT(ISODOW FROM d.dt)::SMALLINT                         AS day_of_week,
    TO_CHAR(d.dt, 'FMDay')                                      AS day_name,
    EXTRACT(DAY FROM d.dt)::SMALLINT                            AS day_of_month,
    EXTRACT(DOY FROM d.dt)::SMALLINT                            AS day_of_year,
    EXTRACT(WEEK FROM d.dt)::SMALLINT                           AS week_of_year,
    EXTRACT(MONTH FROM d.dt)::SMALLINT                          AS month_number,
    TO_CHAR(d.dt, 'FMMonth')                                    AS month_name,
    EXTRACT(QUARTER FROM d.dt)::SMALLINT                        AS quarter_number,
    'Q' || EXTRACT(QUARTER FROM d.dt)::TEXT                     AS quarter_name,
    EXTRACT(YEAR FROM d.dt)::INTEGER                            AS year_number,
    (EXTRACT(ISODOW FROM d.dt) IN (6, 7))                       AS is_weekend,
    (d.dt = (DATE_TRUNC('month', d.dt) + INTERVAL '1 month - 1 day')::DATE)
                                                                AS is_month_end,
    TO_CHAR(d.dt, 'YYYY-MM')                                    AS year_month,
    'public'                                                    AS source_system,
    NOW()                                                       AS etl_loaded_at,
    NOW()                                                       AS created_at,
    NOW()                                                       AS updated_at
FROM (
    SELECT generate_series(
        (SELECT LEAST(
            (SELECT MIN(order_date::DATE) FROM public.orders),
            (SELECT MIN(shipping_date::DATE) FROM public.shipments WHERE shipping_date IS NOT NULL)
        )),
        (SELECT GREATEST(
            (SELECT MAX(order_date::DATE) FROM public.orders),
            (SELECT MAX(shipping_date::DATE) FROM public.shipments WHERE shipping_date IS NOT NULL)
        )),
        INTERVAL '1 day'
    )::DATE AS dt
) d
WHERE NOT EXISTS (
    SELECT 1 FROM warehouse.dim_date x WHERE x.date_key = TO_CHAR(d.dt, 'YYYYMMDD')::INTEGER
);
