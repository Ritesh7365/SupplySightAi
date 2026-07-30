# SupplySight AI — Analytics Layer

Enterprise reporting views and materialized views in the PostgreSQL **`analytics`** schema.

All objects read from the **`warehouse`** star schema only. Warehouse and `public` tables are never modified.

## Layout

```
database/analytics/
├── README.md
├── view_dictionary.md
├── build_analytics.py
├── views/
│   ├── 01_vw_executive_dashboard.sql
│   ├── 02_vw_sales_performance.sql
│   ├── 03_vw_customer_performance.sql
│   ├── 04_vw_product_performance.sql
│   ├── 05_vw_shipping_performance.sql
│   └── 06_vw_geographic_performance.sql
└── materialized/
    ├── 01_mv_monthly_sales.sql
    ├── 02_mv_customer_sales.sql
    └── 03_mv_product_sales.sql
```

## Quick start

```bash
# Requires warehouse tables populated
python database/analytics/build_analytics.py
```

| Flag | Effect |
|------|--------|
| `--views-only` | Create / replace regular views only |
| `--matviews-only` | Create materialized views only |
| `--refresh` | `REFRESH MATERIALIZED VIEW` on existing MVs |

## Objects

### Views (live query warehouse)

| View | Dashboard use |
|------|----------------|
| `vw_executive_dashboard` | KPI strip: sales, profit, orders, customers, AOV, late % |
| `vw_sales_performance` | Trends by month / year / region / market |
| `vw_customer_performance` | Top customers, revenue, AOV, segments |
| `vw_product_performance` | Best / lowest products, profit, category |
| `vw_shipping_performance` | Mode, delays, late risk, avg transit days |
| `vw_geographic_performance` | Sales by country / state / city |

### Materialized views (pre-aggregated)

| Materialized view | Grain | Refresh |
|-------------------|-------|---------|
| `mv_monthly_sales` | Year-month | After warehouse ETL |
| `mv_customer_sales` | Customer | After warehouse ETL |
| `mv_product_sales` | Product | After warehouse ETL |

```sql
REFRESH MATERIALIZED VIEW analytics.mv_monthly_sales;
REFRESH MATERIALIZED VIEW analytics.mv_customer_sales;
REFRESH MATERIALIZED VIEW analytics.mv_product_sales;
```

Or: `python database/analytics/build_analytics.py --refresh`

## Example queries

```sql
-- Executive KPIs
SELECT * FROM analytics.vw_executive_dashboard;

-- Top 10 customers
SELECT customer_name, customer_segment, revenue, average_order_value
FROM analytics.vw_customer_performance
WHERE revenue_rank <= 10
ORDER BY revenue_rank;

-- Monthly trend (fast path)
SELECT year_month, sales, profit, order_count
FROM analytics.mv_monthly_sales
ORDER BY year_month;

-- Late delivery by shipping mode
SELECT shipping_mode, late_delivery_risk_pct, avg_shipping_time_days
FROM analytics.vw_shipping_performance
ORDER BY late_delivery_risk_pct DESC;
```

## Notes

- Earlier `analytics.v_*` / `mv_*` objects from the OLTP (`public`) bootstrap may still exist; this layer uses the `vw_*` / new `mv_*` naming for the **warehouse-backed** enterprise BI surface.
- See [view_dictionary.md](view_dictionary.md) for column-level definitions.
- Dashboards are intentionally out of scope for this milestone.
