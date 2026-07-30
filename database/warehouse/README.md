# SupplySight AI — Enterprise Data Warehouse (Star Schema)

Dimensional model in the PostgreSQL **`warehouse`** schema, populated exclusively from the normalized **`public`** OLTP tables.

## Layout

```
database/warehouse/
├── README.md
├── build_warehouse.py          # Apply DDL + ETL against PostgreSQL
├── schema/                     # CREATE TABLE (+ indexes)
│   ├── 01_dim_date.sql … 07_dim_shipping.sql
│   ├── 08_fact_sales.sql
│   ├── 09_fact_shipments.sql
│   └── 10_indexes.sql
├── etl/                        # INSERT … SELECT from public
│   ├── 00_truncate_warehouse.sql
│   ├── 01_load_dim_date.sql … 07_load_dim_shipping.sql
│   ├── 08_load_fact_sales.sql
│   ├── 09_load_fact_shipments.sql
│   └── 10_validate.sql
└── documentation/
    ├── star_schema.md
    ├── star_schema_diagram.md
    ├── data_dictionary.md
    └── etl_design.md
```

## Quick start

```bash
# From project root (requires .env / PostgreSQL with public data loaded)
python database/warehouse/build_warehouse.py
```

Flags:

| Flag | Effect |
|------|--------|
| `--ddl-only` | Create tables/indexes only |
| `--etl-only` | Run ETL only (tables must exist) |
| `--full-refresh` | Truncate warehouse tables before load |
| `--skip-validate` | Skip post-load validation queries |

## Design summary

| Object | Grain | Source |
|--------|-------|--------|
| `dim_date` | Calendar day | Generated from min/max of `orders` / `shipments` dates |
| `dim_department` | Department | `public.departments` |
| `dim_category` | Category | `public.categories` |
| `dim_product` | Product card | `public.products` |
| `dim_customer` | Customer | `public.customers` (no password) |
| `dim_location` | Distinct order geography | Deduplicated `public.orders` geo fields |
| `dim_shipping` | Shipping mode | Distinct `public.shipments.shipping_mode` |
| `fact_sales` | Order line | `order_items` ⊕ dims |
| `fact_shipments` | Shipment / order | `shipments` ⊕ dims |

**Constraints:** `public` is never modified. Raw CSV is not used. Dimension natural keys are unique; fact loads are guarded with `NOT EXISTS` / unique constraints to avoid duplicate rows.

See [documentation/star_schema.md](documentation/star_schema.md) and the Mermaid diagram in [documentation/star_schema_diagram.md](documentation/star_schema_diagram.md).
