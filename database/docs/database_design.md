# SupplySight AI — Database Design

**Role lens:** Principal Data Engineer / Database Architect  
**Engine:** PostgreSQL  
**Source:** DataCo Supply Chain Dataset (order-item grain extract)

---

## 1. Design Goals

1. **Normalize** repeated customer, product, category, and department attributes out of the flat CSV.
2. Preserve a clear **analytic grain** at `order_items` for BI and ML feature joins.
3. Separate **logistics** (`shipments`) from commercial order headers.
4. Reserve **inventory / warehouse / vendor** structures for future supply-chain optimization without fabricating data now.
5. Remain compatible with FastAPI/SQLAlchemy + Alembic later.

---

## 2. Why Each Table Exists

| Table | Why it exists |
|-------|----------------|
| `departments` | Stable merchandising hierarchy root; avoids repeating department names on every line. |
| `categories` | Product taxonomy; bridges departments ↔ products. |
| `products` | Catalog of sellable items; holds price/status/media independent of orders. |
| `customers` | Party master for segmentation, geo, and PII isolation. |
| `orders` | Order header (status, market, ship-to geo, dates, payment type). |
| `order_items` | Revenue/margin fact grain matching DataCo row uniqueness (`Order Item Id`). |
| `shipments` | Delivery performance attributes for delay prediction and SLA KPIs. |
| `warehouses` | Future multi-node inventory network. |
| `inventory` | Future on-hand / reserved balances for optimization models. |
| `vendors` (+ `vendor_products`) | Future procurement & vendor-risk analytics. |

---

## 3. Normalization Decisions

### From flat file → 3NF-oriented model

The CSV repeats customer, product, category, and department attributes on every order line. We:

- Deduplicate dimensions on natural keys (`Customer Id`, `Product Card Id`, `Category Id`, `Department Id`, `Order Id`).
- Keep measures on `order_items`.
- Keep delivery fields on `shipments` (1:1 with orders in this extract).

### Category → Department

Source analysis shows each `Category Id` maps to exactly one `Department Id`. Therefore `categories.department_id` is a true FK (not M:N).

### Product Category Id

Always equals `Category Id` in the extract; mapped once as `products.category_id`.

### Benefit / Profit / Sales-per-customer fields

Despite “per order” naming, `Benefit per order` and `Order Profit Per Order` can vary within an `Order Id`. They are stored on **`order_items`** to avoid silently discarding variation. `Sales per customer` is retained on the line as a lineage field (not treated as a maintained customer aggregate).

### Shipments 1:1

`shipments.order_id` is UNIQUE. If multi-package shipments appear later, relax uniqueness and introduce parcel-level keys.

---

## 4. Keys & Relationships

- Natural keys reused from DataCo for core commerce entities (easier lineage and idempotent loads).
- Surrogate keys for `shipments`, `warehouses`, `inventory`, `vendors`.
- FK delete rules: `RESTRICT` on dimensions; `CASCADE` from orders → items/shipments.

See `database/erd/ER_Diagram.md` for cardinality and Mermaid.

---

## 5. Data Types

- Money/measures → `NUMERIC(p,s)` (not float).
- Flags → `SMALLINT` with CHECK (0/1) for late risk / product status.
- Zipcodes → `VARCHAR` (leading zeros / non-US formats).
- Timestamps → `TIMESTAMP` for business event times; `TIMESTAMPTZ` for audit columns.

---

## 6. Analytical Performance Considerations

- Indexes on FKs and common filters (status, market/region, shipping mode, late risk, order_date) in `11_indexes.sql`.
- Model is star-join friendly: `order_items` fact → `orders` / `products` / `customers` / `shipments`.
- Future: BRIN/range partition on order date via join table or denormalized `order_date` on items if needed (not done yet).

---

## 7. Future Expansion Strategy

| Phase | Addition |
|-------|----------|
| Next | Load ETL CSVs into Postgres; validate FK orphans = 0 |
| +1 | Synthetic or ERP warehouse + inventory snapshots |
| +1 | Vendor master + lead times for risk scoring |
| +2 | Slowly changing dimensions (SCD2) for product price/status |
| +2 | Event tables for shipment scan telemetry |
| +3 | Mart layer (`mart.daily_sales`, `mart.delivery_kpi`) for BI |

---

## 8. Explicit Non-Goals (this phase)

- No PostgreSQL inserts yet (CSV export only).
- No fabricated warehouse/inventory/vendor business rows.
- No column renames in the raw CSV.
- No dashboards, APIs, or ML models.
