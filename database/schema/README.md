# database/schema

## Purpose

PostgreSQL DDL for the SupplySight AI relational model: dimensions, facts, logistics, and placeholder inventory/vendor entities.

## Contents

| File | Object |
|------|--------|
| `01_departments.sql` | Department dimension |
| `02_categories.sql` | Category dimension (+ FK department) |
| `03_products.sql` | Product catalog |
| `04_customers.sql` | Customer master (PII-sensitive) |
| `05_orders.sql` | Order header |
| `06_order_items.sql` | Order line facts (analytic grain) |
| `07_shipments.sql` | Shipment / delivery profile |
| `08_warehouses.sql` | **Placeholder** warehouse master |
| `09_inventory.sql` | **Placeholder** inventory balances |
| `10_vendors.sql` | **Placeholder** vendors + vendor_products |
| `11_indexes.sql` | Supporting indexes |

## Apply order

Run files in numeric order (`01` → `11`) against an empty database/schema.

## Future implementation

- Alembic migrations mirroring this DDL under `backend/`
- Partitioning strategy for `order_items` by `order_date` (via order join) when volume grows
- RLS policies on `customers` for PII
