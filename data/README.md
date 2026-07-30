# Data — SupplySight AI

## Purpose

Project data lake layout for raw ingestion, cleaned/processed datasets, external reference data, and small sample files used in demos and tests.

## Contents

| Path | Role |
|------|------|
| `raw/` | Immutable source extracts (gitignored payloads) |
| `processed/` | Cleaned/feature-ready datasets |
| `external/` | Third-party or reference datasets |
| `sample/` | Small anonymized samples safe for docs/CI |

## Future Implementation

- Data contracts and column dictionaries in `docs/database/`
- Ingestion scripts under `scripts/`
- PII handling and retention policy

> Large files are ignored; keep only structure and samples as approved.
