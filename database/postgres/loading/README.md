# database/postgres/loading

## Purpose

Enterprise-grade loader that inserts **normalized** CSVs from
`database/normalized_data/` into the PostgreSQL **`public`** schema.

## Modules

| File | Role |
|------|------|
| `config.py` | Load order, PK map, paths |
| `copy_load.py` | COPY + INSERT fallback, truncate, progress |
| `validate.py` | Null/duplicate PK + FK orphan checks, COUNT(*) |
| `report.py` | Writes `reports/load_report.md` |
| `pipeline.py` | Transactional orchestrator |

## Run

```bash
python database/postgres/load_normalized_csv.py
# or
python database/postgres/loading/pipeline.py
```

## Behaviour

1. Ensures `vendor_products.csv` header file exists  
2. Opens a DB transaction  
3. Truncates tables in reverse FK order (`CASCADE`)  
4. Loads each table (COPY → INSERT fallback via SAVEPOINT)  
5. Validates PKs and FKs  
6. Commits on success / rolls back on failure  
7. Writes `database/postgres/reports/load_report.md`

Does **not** load the raw DataCo file. Does **not** clean business values.
