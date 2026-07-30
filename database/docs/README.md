# database/docs

## Purpose

Authoritative documentation for the SupplySight AI relational database: design rationale, ER narrative, and DataCo column mapping.

## Contents

| Document | Description |
|----------|-------------|
| `database_design.md` | Normalization decisions, keys, expansion plan |
| `data_mapping.md` | Every DataCo column → table.column |

## Future implementation

- Data dictionary generated from `information_schema`
- DDL change log aligned with Alembic revisions
