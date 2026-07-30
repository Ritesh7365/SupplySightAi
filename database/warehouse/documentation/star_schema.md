# Star Schema Design — SupplySight AI Warehouse

## Architecture

The warehouse implements a **classic star schema** in PostgreSQL schema `warehouse`:

- **Seven dimensions** surround two fact tables.
- Facts store **surrogate foreign keys** only (plus degenerate keys for drill-through).
- All population is **`INSERT … SELECT` from `public`** — no CSV, no mutation of OLTP tables.

```
                    dim_date
                       │
dim_customer ──┐       │       ┌── dim_product
               │       │       │
dim_location ──┼── fact_sales ─┼── dim_category
               │       │       │
dim_shipping ──┘       │       └── dim_department
                       │
              fact_shipments
                 │    │
        dim_shipping  dim_customer
                 │
              dim_date
```

## Fact grains

### `fact_sales`

| Aspect | Definition |
|--------|------------|
| Grain | One row per **order item** (`order_item_id`) |
| Degenerate keys | `order_id`, `order_item_id` |
| Measures | `quantity`, `sales`, `discount`, `profit`, `profit_ratio` |
| Time | `date_key` ← `orders.order_date` |

### `fact_shipments`

| Aspect | Definition |
|--------|------------|
| Grain | One row per **shipment** (`source_shipment_id` ← `shipments.shipment_id`) |
| Degenerate keys | `order_id`, `source_shipment_id` |
| Measures | `actual_days`, `scheduled_days`, `late_delivery` |
| Time | `date_key` ← `orders.order_date` (aligned with sales) |

## Dimension keys

| Dimension | Surrogate PK | Natural / business key |
|-----------|--------------|-------------------------|
| `dim_date` | `date_key` (YYYYMMDD) | `calendar_date` |
| `dim_department` | `department_key` | `department_id` |
| `dim_category` | `category_key` | `category_id` |
| `dim_product` | `product_key` | `product_id` |
| `dim_customer` | `customer_key` | `customer_id` |
| `dim_location` | `location_key` | `location_bk` (MD5 of geo attrs) |
| `dim_shipping` | `shipping_key` | `shipping_mode` |

Every dimension includes audit columns: `source_system`, `etl_loaded_at`, `created_at`, `updated_at` (and `source_updated_at` where the OLTP row has `updated_at`).

## Referential integrity

Foreign keys are declared on both facts to all referenced dimensions (`ON DELETE RESTRICT`). Load order is dimensions → facts. Full refresh truncates facts first, then dimensions.

## Anti-duplication

- Dimension natural keys are `UNIQUE`.
- Fact loads use `WHERE NOT EXISTS (...)` against natural lineage keys.
- `fact_sales.order_item_id` and `fact_shipments.source_shipment_id` are unique.
- `dim_location` stores **distinct** geographies only (not one row per order).

## Out of scope

- No changes to `public` tables
- No dashboards / BI semantic layer (beyond this schema)
- No ML feature tables in `ml`
- No Type-2 SCD (current load is Type-1 / insert-if-missing; full refresh supported)
