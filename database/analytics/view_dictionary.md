# Analytics View Dictionary

All objects live in schema **`analytics`** and query **`warehouse`** only.

---

## Regular views

### `vw_executive_dashboard`

| Column | Type | Description |
|--------|------|-------------|
| `total_sales` | NUMERIC | Sum of line sales |
| `total_profit` | NUMERIC | Sum of line profit |
| `total_orders` | BIGINT | Distinct `order_id` |
| `total_customers` | BIGINT | Distinct customers with sales |
| `average_order_value` | NUMERIC | `total_sales / total_orders` |
| `late_delivery_pct` | NUMERIC | % of shipments with `late_delivery = 1` |
| `total_shipments` | BIGINT | Shipment count |
| `late_shipments` | BIGINT | Late shipment count |
| `overall_profit_margin_pct` | NUMERIC | Profit ÷ sales × 100 |
| `refreshed_at` | TIMESTAMPTZ | Query-time stamp |

**Grain:** 1 row.  
**Example:** `SELECT * FROM analytics.vw_executive_dashboard;`

---

### `vw_sales_performance`

| Column | Description |
|--------|-------------|
| `year_number`, `month_number`, `year_month`, `month_name` | Calendar attributes |
| `quarter_number`, `quarter_name` | Quarter attributes |
| `market`, `region` | Geography from `dim_location` |
| `sales`, `profit`, `discount` | Aggregated measures |
| `units_sold`, `order_count`, `customer_count`, `line_count` | Volume metrics |
| `average_order_value`, `profit_margin_pct` | Derived KPIs |

**Grain:** year × month × market × region.  
**Dashboard tips:**

- Sales by Month → `GROUP BY year_month` or filter one market
- Sales by Year → `GROUP BY year_number`
- Sales by Region / Market → `GROUP BY region` / `market`

---

### `vw_customer_performance`

| Column | Description |
|--------|-------------|
| `customer_key`, `customer_id`, `customer_name` | Customer identity |
| `customer_segment` | Consumer / Corporate / Home Office |
| `customer_city`, `customer_state`, `customer_country` | Customer geo |
| `revenue`, `profit`, `discount` | Customer totals |
| `order_count`, `units_purchased` | Volume |
| `average_order_value`, `profit_margin_pct` | Derived |
| `revenue_rank` | Global rank by revenue (1 = top) |
| `segment_revenue_rank` | Rank within segment |

**Grain:** 1 row per customer.  
**Top customers:** `WHERE revenue_rank <= 20`.

---

### `vw_product_performance`

| Column | Description |
|--------|-------------|
| Product / category / department keys & names | Dimensional attributes |
| `sales`, `profit`, `discount`, `units_sold` | Measures |
| `order_count`, `customer_count` | Reach metrics |
| `profit_margin_pct` | Margin |
| `best_selling_rank` | 1 = highest sales |
| `lowest_selling_rank` | 1 = lowest sales |
| `profit_rank` | 1 = highest profit |
| `category_sales_rank` | Rank within category |
| `category_total_sales`, `category_total_profit` | Category rollups |

**Grain:** 1 row per product.  
**Best / lowest:** filter `best_selling_rank` / `lowest_selling_rank`.

---

### `vw_shipping_performance`

| Column | Description |
|--------|-------------|
| `shipping_mode`, `shipping_mode_group` | Mode dimension |
| `shipment_count`, `order_count`, `customer_count` | Volume |
| `avg_shipping_time_days` | Avg `actual_days` |
| `avg_scheduled_days` | Avg scheduled days |
| `avg_delivery_delay_days` | Avg (actual − scheduled) |
| `delayed_shipment_count`, `delay_rate_pct` | actual > scheduled |
| `late_delivery_count`, `late_delivery_risk_pct` | From `late_delivery` flag |
| `*_status_count` | Counts by `delivery_status` label |

**Grain:** 1 row per shipping mode.

---

### `vw_geographic_performance`

| Column | Description |
|--------|-------------|
| `market`, `region`, `country`, `state`, `city` | Order destination |
| `sales`, `profit`, `discount`, `units_sold` | Measures |
| `order_count`, `customer_count`, `average_order_value` | Volume / AOV |
| `profit_margin_pct` | Margin |
| `geo_sales_rank` | Global rank by sales |
| `country_city_sales_rank` | Rank within country |

**Grain:** country × state × city (+ market/region).  
**By country only:** `SELECT country, SUM(sales) ... GROUP BY country`.

---

## Materialized views

### `mv_monthly_sales`

Pre-aggregated monthly sales/profit/orders/AOV/margin.  
**Unique index:** `year_month`.

### `mv_customer_sales`

Pre-aggregated customer sales/profit/orders/AOV.  
**Unique index:** `customer_key`. Indexes on `customer_segment`, `sales DESC`.

### `mv_product_sales`

Pre-aggregated product sales/profit/units with category & department.  
**Unique index:** `product_key`. Indexes on `category_id`, `sales DESC`.

**Refresh after warehouse load:**

```sql
REFRESH MATERIALIZED VIEW analytics.mv_monthly_sales;
REFRESH MATERIALIZED VIEW analytics.mv_customer_sales;
REFRESH MATERIALIZED VIEW analytics.mv_product_sales;
```

---

## Lineage

```
warehouse.fact_sales / fact_shipments / dims
        │
        ▼
analytics.vw_*  (live)
analytics.mv_*  (snapshot; refresh explicitly)
```

Warehouse tables are **not** modified by this layer.
