# Operations master tables

`warehouses.csv`, `inventory.csv`, `vendors.csv`, and `vendor_products.csv` remain
header-only in `normalized_data/` because the DataCo extract has no WMS / SRM keys.

**Automatic population:** after a successful commerce CSV load, the pipeline runs:

```bash
python database/postgres/seed_operations_masters.py
```

(also invoked automatically from `loading/pipeline.py`).

This seeds:

| Table | Typical volume |
|-------|----------------|
| `public.warehouses` | 20 sites across Americas / EMEA / APAC |
| `public.inventory` | every product × every warehouse |
| `public.vendors` | 50 suppliers |
| `public.vendor_products` | 2–5 vendors per product |

Schema extensions (capacity, utilization, safety stock, vendor rating, etc.) live in
`database/schema/12_ops_master_extensions.sql`.
