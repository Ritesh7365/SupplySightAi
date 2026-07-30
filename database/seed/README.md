# database/seed

## Purpose

Holds normalized CSV extracts produced by `database/etl/` for later PostgreSQL loading (`COPY` / bulk insert).

## Contents (after ETL run)

| File | Source |
|------|--------|
| `departments.csv` | Deduplicated DataCo departments |
| `categories.csv` | Deduplicated categories |
| `products.csv` | Deduplicated products |
| `customers.csv` | Deduplicated customers |
| `orders.csv` | Deduplicated order headers |
| `order_items.csv` | Full order-line facts |
| `shipments.csv` | One shipment profile per order |

**Not generated from DataCo:** warehouses, inventory, vendors (placeholder schemas only).

## Future implementation

- `psql \copy` scripts under `scripts/database/`
- Idempotent upsert loaders
