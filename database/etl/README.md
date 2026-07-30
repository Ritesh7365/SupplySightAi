# SupplySight AI — ETL Package

## Purpose

Production-style **Extract → Transform → Load** pipeline that converts the flat
DataCo supply-chain CSV into normalized CSV files matching the PostgreSQL schema.

**This phase does not connect to PostgreSQL.**

## Layout

```
database/etl/
├── config.py          # Paths, encodings, table registries
├── utils.py           # Logging + helpers
├── extract.py         # Read + validate raw CSV
├── transform.py       # Structural normalization + FK checks
├── load.py            # Write CSVs to normalized_data/
├── pipeline.py        # Orchestrator (entry point)
├── logs/              # Runtime logs (generated)
└── README.md

database/normalized_data/   # CSV outputs (generated)
```

## Run

From the `database/etl` directory:

```bash
python pipeline.py
```

Or from the project root:

```bash
python database/etl/pipeline.py
```

## Pipeline flow

```
Extract  →  validate file / encoding / row & column counts
    ↓
Transform → split dimensions + facts, dedupe dimensions, preserve order_items
    ↓
Load     → write CSVs under database/normalized_data/
```

## Outputs

| File | Source |
|------|--------|
| `departments.csv` | DataCo (deduped) |
| `categories.csv` | DataCo (deduped) |
| `products.csv` | DataCo (deduped) |
| `customers.csv` | DataCo (deduped) |
| `orders.csv` | DataCo (deduped headers) |
| `order_items.csv` | DataCo (all transactional rows) |
| `shipments.csv` | DataCo (1 per order) |
| `warehouses.csv` | **Headers only** (later phase) |
| `inventory.csv` | **Headers only** (later phase) |
| `vendors.csv` | **Headers only** (later phase) |

See `database/normalized_data/PLACEHOLDER_TABLES.md` for placeholder documentation.

## Rules

- Deduplicate **dimension** keys only
- Do **not** drop transactional `order_items` rows
- Do **not** modify business measure values
- Do **not** fabricate warehouse / inventory / vendor records
- Do **not** connect to PostgreSQL yet

## Extending

1. Add new mappings in `transform.py`
2. Register output names in `config.POPULATED_TABLES` or `PLACEHOLDER_TABLES`
3. Keep Postgres loaders as a future `load_postgres.py` module
