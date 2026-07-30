# database/

## Purpose

Enterprise PostgreSQL design assets for SupplySight AI: DDL, ER docs, DataCo mapping, ETL-to-CSV, and seed outputs.

## Layout

```
database/
├── schema/     # CREATE TABLE + indexes (01–11)
├── erd/        # ER diagram (Mermaid + narrative)
├── docs/       # Design + column mapping
├── etl/        # Normalize DataCo → relational CSVs
└── seed/       # Exported CSV tables (post-ETL)
```

## Quick start

1. Review `docs/database_design.md` and `erd/ER_Diagram.md`
2. Run the modular ETL:
   ```bash
   python database/etl/pipeline.py
   ```
3. Inspect CSVs under `database/normalized_data/`
4. Initialize PostgreSQL (schemas + DDL + views — **no CSV load**):
   ```bash
   python database/postgres/initialize.py
   ```
5. Apply/verify report: `database/postgres/reports/verification_report.md`

## Status

| Area | Status |
|------|--------|
| Commerce schema (customers→shipments) | Designed + ETL CSV export |
| Warehouses / inventory / vendors | Placeholder DDL only |
| Postgres INSERT/COPY | Not in this phase |
