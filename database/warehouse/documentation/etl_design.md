# ETL Design — Warehouse Population

## Principles

1. **Source of truth:** `public.*` only (never raw CSV).
2. **Read-only OLTP:** No `UPDATE` / `DELETE` / DDL against `public`.
3. **Idempotent inserts:** `WHERE NOT EXISTS` on natural keys; unique constraints as safety net.
4. **Referential integrity:** Load dimensions before facts; FKs enforced in `warehouse`.
5. **No dimensional duplication:** Locations and shipping modes are distinct sets, not per-order copies.

## Load sequence

| Step | Script | Target |
|------|--------|--------|
| 0 (optional) | `00_truncate_warehouse.sql` | Full refresh |
| 1 | `01_load_dim_date.sql` | `dim_date` |
| 2 | `02_load_dim_department.sql` | `dim_department` |
| 3 | `03_load_dim_category.sql` | `dim_category` |
| 4 | `04_load_dim_product.sql` | `dim_product` |
| 5 | `05_load_dim_customer.sql` | `dim_customer` |
| 6 | `06_load_dim_location.sql` | `dim_location` |
| 7 | `07_load_dim_shipping.sql` | `dim_shipping` |
| 8 | `08_load_fact_sales.sql` | `fact_sales` |
| 9 | `09_load_fact_shipments.sql` | `fact_shipments` |
| 10 | `10_validate.sql` | Diagnostics |

Orchestrated by `database/warehouse/build_warehouse.py`.

## Mapping highlights

| Warehouse column | Public source |
|------------------|---------------|
| `fact_sales.discount` | `order_items.discount_amount` |
| `fact_sales.profit` | `order_items.profit_amount` |
| `fact_sales.date_key` | `orders.order_date` → YYYYMMDD |
| `fact_sales.location_key` | MD5 of order geo attrs → `dim_location` |
| `fact_shipments.actual_days` | `shipments.days_for_shipping_real` |
| `fact_shipments.scheduled_days` | `shipments.days_for_shipment_scheduled` |
| `fact_shipments.late_delivery` | `shipments.late_delivery_risk` |

## Expected row counts (after successful public load)

| Table | Expected ≈ |
|-------|------------|
| `dim_department` | 11 |
| `dim_category` | 51 |
| `dim_product` | 118 |
| `dim_customer` | 20,652 |
| `dim_shipping` | ~4 |
| `dim_location` | distinct order geographies |
| `dim_date` | days between min and max order/ship dates |
| `fact_sales` | 180,519 (= `order_items`) |
| `fact_shipments` | 65,752 (= `shipments`) |

## Incremental vs full refresh

- **Incremental (default):** Inserts only missing natural keys.
- **Full refresh:** `--full-refresh` runs truncate, then full reload (Type-1 snapshot).

Attribute updates on existing dimension keys are **not** applied in incremental mode; use full refresh after OLTP corrections.
