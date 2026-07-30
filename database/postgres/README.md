# database/postgres — PostgreSQL Initialization

## Purpose

Production-style initialization for the **supplysight_ai** PostgreSQL database:

1. Connect via environment variables  
2. Create logical schemas (`staging`, `warehouse`, `analytics`, `ml`)  
3. Apply DDL from `database/schema/` into **`public`**  
   (`warehouse` stays empty for a later fact/dimension phase)  
4. Create analytics views and materialized views  
5. Verify objects and write a Markdown report  

**CSV loading is intentionally disabled in this phase.**

---

## Modules

| File | Responsibility |
|------|----------------|
| `connection.py` | Env-based connection + reusable migration helpers |
| `create_schemas.py` | Create platform schemas |
| `execute_schema_files.py` | Run `01_*.sql` … `11_indexes.sql` in order |
| `create_views.py` | Analytics views on public tables |
| `create_materialized_views.py` | KPI materialized views (`WITH NO DATA`) |
| `verify_database.py` | Tables / PKs / FKs / indexes / row counts report |
| `load_normalized_csv.py` | Future CSV loader (`--execute` required) |
| `initialize.py` | One-shot orchestrator (no CSV load) |
| `README.md` | This document |

Reusable helpers in `connection.py`:

- `connect`, `get_connection`, `get_cursor`
- `execute_sql`, `execute_sql_script`, `run_sql_file`
- `ensure_schema`, `schema_exists`, `table_exists`
- `set_search_path`, `list_sql_files`

---

## Environment

Set in `.env` (see root `.env.example`):

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=supplysight_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
# Optional:
# DATABASE_URL=postgresql://user:pass@localhost:5432/supplysight_ai
```

Dependencies: `psycopg2-binary`, `python-dotenv`, `pandas` (pandas only for future CSV load).

```bash
pip install psycopg2-binary python-dotenv pandas
```

---

## Recommended run order

```bash
# From project root
python database/postgres/create_schemas.py
python database/postgres/execute_schema_files.py
python database/postgres/create_views.py
python database/postgres/create_materialized_views.py
python database/postgres/verify_database.py
```

Or all at once (still **no** CSV load):

```bash
python database/postgres/initialize.py
```

Report output:

`database/postgres/reports/verification_report.md`

---

## Schema layout

| Schema | Role |
|--------|------|
| `public` | **Current DDL target** — normalized relational tables from `database/schema/` |
| `staging` | Future raw / landing loads |
| `warehouse` | Reserved for future fact/dimension tables (**empty for now**) |
| `analytics` | Views + materialized views for BI |
| `ml` | Future feature / scoring tables |

DDL files under `database/schema/` are applied with:

`SET search_path TO public;`

so existing SQL creates objects in `public`.

---

## CSV load

```bash
python database/postgres/load_normalized_csv.py
```

Loads `database/normalized_data/*.csv` into **`public`** (COPY with INSERT fallback),
validates PKs/FKs, and writes `database/postgres/reports/load_report.md`.

After a successful load you may refresh mat views:

```sql
REFRESH MATERIALIZED VIEW analytics.mv_daily_sales;
REFRESH MATERIALIZED VIEW analytics.mv_late_delivery_by_mode;
```

---

## Out of scope (this module)

- Dashboarding  
- ML model training  
- Loading the raw DataCo CSV  
- Cleaning / transforming business values  
