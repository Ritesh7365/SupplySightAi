# SupplySight AI — Data Understanding Report

**Project:** SupplySight AI – Intelligent Supply Chain Analytics & Inventory Optimization Platform  
**Phase:** Data Understanding (EDA)  
**Date:** 2026-07-30  
**Analyst Role:** Senior Data Scientist / Senior Data Engineer  
**Scope:** Read-only profiling of raw DataCo Supply Chain datasets. No cleaning or modeling performed.

---

## 1. Executive Summary

The primary transactional dataset (`DataCoSupplyChainDataset.csv`) contains **180,519 rows** and **53 columns**, covering order-line commerce events with customer, product, shipping, geography, sales, and profit attributes.

A companion dictionary file (`DescriptionDataCoSupplyChain.csv`) documents **52 field descriptions**.

Key data-quality observations at a glance:

- **Missing values:** 4 column(s) contain nulls (see Section 4).
- **Duplicate rows:** 0 (0.0%).
- **Date fields detected:** order date (DateOrders), shipping date (DateOrders).
- **Memory footprint (deep):** ~299.94 MB.

This report establishes the factual baseline required before any cleaning, feature engineering, or ML work.

---

## 2. Dataset Overview

| Attribute | Value |
|-----------|-------|
| Main file | `data/raw/data/DataCoSupplyChainDataset.csv` |
| Description file | `data/raw/data/DescriptionDataCoSupplyChain.csv` |
| Rows | 180,519 |
| Columns | 53 |
| Memory (deep) | 299.94 MB |
| Encoding used | latin-1 |

### Column families present

| Domain | Present |
|--------|---------|
| Orders / order items | Yes |
| Customers | Yes |
| Products / categories | Yes |
| Shipping / logistics | Yes |
| Sales / profit | Yes |
| Geography | Yes |
| Late delivery risk | Yes |

Artifacts generated under `analysis/output/` include column, missing, duplicate, statistics, and categorical summaries.

---

## 3. Data Quality Assessment

| Check | Result |
|-------|--------|
| Schema consistency | 53 typed columns; mixed object/int/float |
| Completeness | 4 columns with missing values |
| Uniqueness (full-row) | 0.0% duplicate rows |
| ID cardinality | Multiple identifier columns present (Customer Id, Order Id, Order Item Id, Product Card Id, etc.) |
| Sensitive fields | Customer Email / Password columns exist — treat as PII for future governance |
| Description coverage | Dictionary has 52 field docs vs 53 dataset columns |

**Overall quality posture:** Usable for analytics prototyping, but several completeness and governance issues must be addressed before production modeling or KPI dashboards.

---

## 4. Missing Values Summary

Columns with missing values (top 15 by count):

| Column              |   Missing Values |   Missing Percentage |
|:--------------------|-----------------:|---------------------:|
| Product Description |           180519 |             100      |
| Order Zipcode       |           155679 |              86.2397 |
| Customer Lname      |                8 |               0.0044 |
| Customer Zipcode    |                3 |               0.0017 |

Visualizations: `analysis/output/figures/missingno_matrix.png`, `missingno_bar.png`.  
CSV: `analysis/output/missing_values.csv`.

---

## 5. Duplicate Summary

| Metric | Value |
|--------|-------|
| Total rows | 180,519 |
| Duplicate rows | 0 |
| Duplicate % | 0.0 |
| Unique rows | 180,519 |

CSV: `analysis/output/duplicate_report.csv`.

---

## 6. Numerical Features Summary

Descriptive statistics were computed for all numeric columns and saved to `analysis/output/statistics.csv`.

### Outlier spotlight (IQR method, top columns)

| Column                   |   Outlier Count |   Outlier Percentage |
|:-------------------------|----------------:|---------------------:|
| Benefit per order        |           18942 |              10.4931 |
| Order Profit Per Order   |           18942 |              10.4931 |
| Order Item Profit Ratio  |           17300 |               9.5835 |
| Order Item Discount      |            7537 |               4.1752 |
| Order Item Product Price |            2048 |               1.1345 |
| Product Price            |            2048 |               1.1345 |
| Order Item Total         |            1943 |               1.0763 |
| Sales per customer       |            1943 |               1.0763 |

Distribution and boxplot visuals: `numeric_histograms.png`, `numeric_boxplots.png`.

### Notable correlation pairs (absolute value)

| Feature A | Feature B | Correlation |
|-----------|-----------|-------------|
| Benefit per order | Order Profit Per Order | 1.0000 |
| Sales per customer | Order Item Total | 1.0000 |
| Order Item Product Price | Product Price | 1.0000 |
| Sales per customer | Sales | 0.9897 |
| Sales | Order Item Total | 0.9897 |
| Benefit per order | Order Item Profit Ratio | 0.8237 |
| Order Item Profit Ratio | Order Profit Per Order | 0.8237 |
| Order Item Product Price | Sales | 0.7899 |
| Sales | Product Price | 0.7899 |
| Sales per customer | Order Item Product Price | 0.7818 |
| Sales per customer | Product Price | 0.7818 |
| Order Item Product Price | Order Item Total | 0.7818 |

Heatmap: `analysis/output/figures/correlation_heatmap.png`.

---

## 7. Categorical Features Summary

Object / categorical columns profiled in `analysis/output/categorical_summary.csv`.

Preview (top 15 columns by listing order):

| Column            |   Unique Values | Most Frequent           |   Most Frequent Count |
|:------------------|----------------:|:------------------------|----------------------:|
| Type              |               4 | DEBIT                   |                 69295 |
| Delivery Status   |               4 | Late delivery           |                 98977 |
| Category Name     |              50 | Cleats                  |                 24551 |
| Customer City     |             563 | Caguas                  |                 66770 |
| Customer Country  |               2 | EE. UU.                 |                111146 |
| Customer Email    |               1 | XXXXXXXXX               |                180519 |
| Customer Fname    |             782 | Mary                    |                 65150 |
| Customer Lname    |            1109 | Smith                   |                 64104 |
| Customer Password |               1 | XXXXXXXXX               |                180519 |
| Customer Segment  |               3 | Consumer                |                 93504 |
| Customer State    |              46 | PR                      |                 69373 |
| Customer Street   |            7458 | 9126 Wishing Expressway |                   122 |
| Department Name   |              11 | Fan Shop                |                 66861 |
| Market            |               5 | LATAM                   |                 51594 |
| Order City        |            3597 | Santo Domingo           |                  2211 |

High-cardinality columns (e.g., streets, names, product names) will need careful encoding strategies later — **not applied in this phase**.

---

## 8. Business Insights

### Orders
Order-level identifiers (`Order Id`, `Order Item Id`, `Order Status`, `order date (DateOrders)`) indicate an **order-line grain** dataset: one row ≈ one purchased line item within an order.

### Customers
Customer demographics and segments (`Customer Id`, `Customer Segment`, city/state/country, email) enable RFM-style and segment analytics. Password/email fields require privacy controls.

### Products & Categories
`Product Name`, `Product Price`, `Category Name`, `Department Name`, and related IDs support assortment, pricing, and category performance analysis.

### Shipping & Logistics
`Shipping Mode`, `Days for shipping (real)` vs `Days for shipment (scheduled)`, `Delivery Status`, and `Late_delivery_risk` form a strong **delivery performance** and SLA analytics surface.

### Sales & Profit
`Sales`, `Sales per customer`, `Order Item Total`, `Benefit per order`, `Order Profit Per Order`, discounts and profit ratios support revenue/margin monitoring and promotion effectiveness.

### Geography
Customer and order geography (`Market`, `Order Region`, `Order Country`, `Order City`, lat/long) support regional demand and logistics heatmaps.

### Inventory-related signals
Direct on-hand inventory quantities are limited; inventory analytics will likely rely on proxies (order quantities, product velocity, stockout-related status if present) until warehouse stock feeds are integrated.

### Timeline
- **order date (DateOrders)**: min `2015-01-01 00:00:00`, max `2018-01-31 23:38:00`, span `1126` days, non-null `180519`
- **shipping date (DateOrders)**: min `2015-01-03 00:00:00`, max `2018-02-06 22:14:00`, span `1130` days, non-null `180519`


---

## 9. Potential KPIs

| KPI | Business Question |
|-----|-------------------|
| On-time delivery rate | % orders not late (`Late_delivery_risk`, `Delivery Status`) |
| Average shipping delay | Real vs scheduled shipping days |
| Gross sales / net sales | `Sales`, discounts, `Order Item Total` |
| Profit per order / margin % | `Order Profit Per Order`, profit ratio |
| Late delivery rate by shipping mode | Mode × risk |
| Sales by market / region | Geographic revenue mix |
| Customer segment contribution | Segment revenue & profit |
| Category / department performance | Assortment profitability |
| Discount leakage | Discount rate vs profit |
| Order cycle time | Order date → shipping date |

---

## 10. Possible Machine Learning Problems

| Problem | Type | Target / Signal |
|---------|------|-----------------|
| Late delivery prediction | Classification | `Late_delivery_risk` / `Delivery Status` |
| Delivery days forecasting | Regression | `Days for shipping (real)` |
| Demand / sales forecasting | Time series | `Sales` by product/region/date |
| Fraud / cancellation risk | Classification | `Order Status` (canceled patterns) |
| Customer segmentation | Clustering | RFM + segment features |
| Profitability prediction | Regression | `Order Profit Per Order` |
| Shipping mode recommendation | Multiclass | Optimal `Shipping Mode` |
| Product affinity / recommendations | Ranking | Co-purchase patterns |

---

## 11. Data Challenges

1. **Missingness** concentrated in specific columns (see missing report) — may bias delivery or geo analyses.
2. **PII exposure** (`Customer Email`, `Customer Password`) — unsuitable for broad sharing; masking required later.
3. **Order-line grain** can inflate customer/order metrics if analysts treat rows as orders.
4. **High-cardinality categoricals** (streets, names, product titles) complicate encoding.
5. **Potential leakage** for delivery models if post-delivery fields are used naively.
6. **Limited explicit inventory levels** — inventory optimization may need external stock data.
7. **Date parsing / timezone** consistency should be validated before temporal KPIs.
8. **ID vs measure confusion** — many integer ID columns look numeric but are categorical identifiers.

---

## 12. Recommendations Before Data Cleaning

1. **Define canonical grain** (order vs order-item) and document KPI formulas accordingly.
2. **PII policy:** drop or hash email/password before any shared environments.
3. **Treat ID columns as categorical** despite integer dtype.
4. **Profile missingness causes** (system gaps vs true unknowns) before imputation.
5. **Validate date parse formats** for `order date (DateOrders)` and `shipping date (DateOrders)`.
6. **Establish leakage rules** for late-delivery modeling (exclude post-outcome fields).
7. **Join description dictionary** to a data catalog for stakeholder alignment.
8. **Do not rename columns yet** — preserve raw schema until a governed data contract is approved.
9. **Sample stratified QA** across markets/shipping modes before transformations.
10. **Plan inventory data integration** if stock optimization is a Phase-2 priority.

---

## Appendix — Generated Artifacts

| Artifact | Path |
|----------|------|
| Column summary | `analysis/output/column_summary.csv` |
| Missing values | `analysis/output/missing_values.csv` |
| Duplicates | `analysis/output/duplicate_report.csv` |
| Statistics | `analysis/output/statistics.csv` |
| Categorical summary | `analysis/output/categorical_summary.csv` |
| Figures | `analysis/output/figures/` |
| Notebook | `analysis/01_data_understanding.ipynb` |

---

*End of Data Understanding Report — SupplySight AI*
