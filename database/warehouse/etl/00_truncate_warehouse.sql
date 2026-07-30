-- =============================================================================
-- SupplySight AI — Truncate warehouse tables (full refresh helper)
-- Order: facts first, then dimensions (respects FK RESTRICT).
-- Does NOT touch public / staging / analytics / ml.
-- =============================================================================

TRUNCATE TABLE
    warehouse.fact_sales,
    warehouse.fact_shipments
RESTART IDENTITY CASCADE;

TRUNCATE TABLE
    warehouse.dim_date,
    warehouse.dim_department,
    warehouse.dim_category,
    warehouse.dim_product,
    warehouse.dim_customer,
    warehouse.dim_location,
    warehouse.dim_shipping
RESTART IDENTITY CASCADE;
