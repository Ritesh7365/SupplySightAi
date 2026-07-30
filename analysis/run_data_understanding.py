"""
SupplySight AI — Data Understanding Phase
Enterprise-grade exploratory analysis (read-only; no cleaning or transforms that alter source data).
"""

from __future__ import annotations

import warnings
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import missingno as msno
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(r"D:\Data Science Project\SupplySightAi")
RAW_MAIN = ROOT / "data" / "raw" / "data" / "DataCoSupplyChainDataset.csv"
RAW_DESC = ROOT / "data" / "raw" / "data" / "DescriptionDataCoSupplyChain.csv"
ANALYSIS = ROOT / "analysis"
OUTPUT = ANALYSIS / "output"
FIGURES = OUTPUT / "figures"

OUTPUT.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.bbox"] = "tight"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load main dataset and column description dictionary (encoding latin-1 for DataCo)."""
    df = pd.read_csv(RAW_MAIN, encoding="latin-1", low_memory=False)
    desc = pd.read_csv(RAW_DESC, encoding="latin-1")
    return df, desc


def build_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build enterprise column profile: dtype, missing, unique, example."""
    rows = []
    for col in df.columns:
        series = df[col]
        non_null = series.dropna()
        example = non_null.iloc[0] if len(non_null) else np.nan
        missing = int(series.isna().sum())
        rows.append(
            {
                "Column Name": col,
                "Data Type": str(series.dtype),
                "Missing Values": missing,
                "Missing Percentage": round(100.0 * missing / len(df), 4),
                "Unique Values": int(series.nunique(dropna=True)),
                "Example Value": example,
            }
        )
    return pd.DataFrame(rows)


def missing_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Missing value counts and percentages for all columns."""
    missing = df.isna().sum()
    report = pd.DataFrame(
        {
            "Column": missing.index,
            "Missing Values": missing.values,
            "Missing Percentage": np.round(100.0 * missing.values / len(df), 4),
        }
    ).sort_values("Missing Values", ascending=False)
    return report.reset_index(drop=True)


def duplicate_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Full-row duplicate metrics."""
    dup_count = int(df.duplicated().sum())
    return pd.DataFrame(
        [
            {
                "Total Rows": len(df),
                "Duplicate Rows": dup_count,
                "Duplicate Percentage": round(100.0 * dup_count / len(df), 6),
                "Unique Rows": len(df) - dup_count,
            }
        ]
    )


def detect_datetime_columns(df: pd.DataFrame) -> list[str]:
    """Heuristically detect date/datetime columns by name and parseability."""
    candidates = []
    for col in df.columns:
        name_hint = any(
            token in col.lower()
            for token in ("date", "time", "timestamp", "datetime")
        )
        if name_hint:
            candidates.append(col)
            continue
        # sample parse check for object columns
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str).head(50)
            if sample.empty:
                continue
            parsed = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
            if parsed.notna().mean() >= 0.8:
                candidates.append(col)
    return candidates


def outlier_summary(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
    """IQR-based outlier counts per numeric column (analysis only)."""
    rows = []
    for col in numeric_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = int(((s < lower) | (s > upper)).sum())
        rows.append(
            {
                "Column": col,
                "Q1": q1,
                "Q3": q3,
                "IQR": iqr,
                "Lower Bound": lower,
                "Upper Bound": upper,
                "Outlier Count": outliers,
                "Outlier Percentage": round(100.0 * outliers / len(s), 4),
            }
        )
    return pd.DataFrame(rows)


def categorical_summary(df: pd.DataFrame, cat_cols: list[str], top_n: int = 10) -> pd.DataFrame:
    """Unique counts and top categories for categorical/object columns."""
    rows = []
    for col in cat_cols:
        vc = df[col].value_counts(dropna=False).head(top_n)
        top_str = "; ".join([f"{idx} ({cnt})" for idx, cnt in vc.items()])
        rows.append(
            {
                "Column": col,
                "Unique Values": int(df[col].nunique(dropna=True)),
                "Top Categories (value count)": top_str,
                "Most Frequent": vc.index[0] if len(vc) else np.nan,
                "Most Frequent Count": int(vc.iloc[0]) if len(vc) else 0,
            }
        )
    return pd.DataFrame(rows)


def save_numeric_plots(df: pd.DataFrame, numeric_cols: list[str]) -> None:
    """Histograms and boxplots for numeric features (saved to figures/)."""
    # Limit extreme cardinality ID-like columns for readable plots
    plot_cols = [
        c
        for c in numeric_cols
        if df[c].nunique(dropna=True) > 5
        and not c.lower().endswith(" id")
        and c.lower()
        not in {
            "customer id",
            "order id",
            "order item id",
            "order customer id",
            "product card id",
            "order item cardprod id",
            "category id",
            "department id",
            "product category id",
            "customer zipcode",
            "order zipcode",
            "latitude",
            "longitude",
        }
    ]
    # Keep core business metrics even if filtered above
    preferred = [
        "Days for shipping (real)",
        "Days for shipment (scheduled)",
        "Benefit per order",
        "Sales per customer",
        "Late_delivery_risk",
        "Order Item Discount",
        "Order Item Discount Rate",
        "Order Item Product Price",
        "Order Item Profit Ratio",
        "Order Item Quantity",
        "Sales",
        "Order Item Total",
        "Order Profit Per Order",
        "Product Price",
        "Product Status",
    ]
    plot_cols = [c for c in preferred if c in df.columns] or plot_cols[:12]

    # Histograms grid
    n = len(plot_cols)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(14, 3.2 * rows))
    axes = np.array(axes).reshape(-1)
    for i, col in enumerate(plot_cols):
        axes[i].hist(df[col].dropna(), bins=40, color="#1f4e79", alpha=0.85, edgecolor="white")
        axes[i].set_title(col, fontsize=9)
        axes[i].tick_params(labelsize=7)
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")
    fig.suptitle("Numerical Feature Distributions (Histograms)", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES / "numeric_histograms.png")
    plt.close(fig)

    # Boxplots grid
    fig, axes = plt.subplots(rows, cols, figsize=(14, 3.2 * rows))
    axes = np.array(axes).reshape(-1)
    for i, col in enumerate(plot_cols):
        axes[i].boxplot(df[col].dropna(), vert=True, patch_artist=True)
        axes[i].set_title(col, fontsize=9)
        axes[i].tick_params(labelsize=7)
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")
    fig.suptitle("Numerical Feature Boxplots (Outlier View)", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES / "numeric_boxplots.png")
    plt.close(fig)


def save_missing_plot(df: pd.DataFrame) -> None:
    """missingno matrix and bar chart."""
    # Focus on columns with any missing to keep plot readable
    miss_cols = df.columns[df.isna().any()].tolist()
    sample = df if len(df) <= 5000 else df.sample(5000, random_state=42)
    plot_df = sample[miss_cols] if miss_cols else sample.iloc[:, :20]

    fig = msno.matrix(plot_df, figsize=(14, 6), fontsize=9)
    plt.title("Missing Value Matrix (sample)", fontsize=12)
    plt.savefig(FIGURES / "missingno_matrix.png")
    plt.close("all")

    fig = msno.bar(plot_df, figsize=(14, 6), fontsize=9)
    plt.title("Missing Value Bars (sample)", fontsize=12)
    plt.savefig(FIGURES / "missingno_bar.png")
    plt.close("all")


def save_correlation(df: pd.DataFrame, numeric_cols: list[str]) -> tuple[pd.DataFrame, list[tuple]]:
    """Correlation matrix + heatmap; return top absolute correlations."""
    # Prefer business metrics over raw IDs
    exclude = {
        "customer id",
        "order id",
        "order item id",
        "order customer id",
        "product card id",
        "order item cardprod id",
        "category id",
        "department id",
        "product category id",
        "customer zipcode",
        "order zipcode",
    }
    corr_cols = [c for c in numeric_cols if c.lower() not in exclude]
    if len(corr_cols) < 2:
        corr_cols = numeric_cols
    corr = df[corr_cols].corr(numeric_only=True)

    plt.figure(figsize=(14, 11))
    sns.heatmap(
        corr,
        cmap="RdBu_r",
        center=0,
        annot=False,
        square=True,
        linewidths=0.2,
        cbar_kws={"shrink": 0.7},
    )
    plt.title("Correlation Heatmap — Numerical Features", fontsize=13)
    plt.tight_layout()
    plt.savefig(FIGURES / "correlation_heatmap.png")
    plt.close()

    # Pairwise absolute correlations
    pairs = []
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr.iloc[i, j]
            if pd.notna(val):
                pairs.append((cols[i], cols[j], float(val)))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    return corr, pairs[:20]


def write_report(
    df: pd.DataFrame,
    desc: pd.DataFrame,
    col_summary: pd.DataFrame,
    missing_report: pd.DataFrame,
    dup_report: pd.DataFrame,
    stats: pd.DataFrame,
    cat_summary: pd.DataFrame,
    date_cols: list[str],
    date_info: dict,
    outlier_df: pd.DataFrame,
    top_corrs: list[tuple],
) -> None:
    """Write professional Data Understanding Report markdown."""
    miss_cols = missing_report[missing_report["Missing Values"] > 0]
    mem_mb = df.memory_usage(deep=True).sum() / (1024**2)

    # High-level business field presence
    def has(*names: str) -> bool:
        lower = {c.lower(): c for c in df.columns}
        return any(n.lower() in lower for n in names)

    top_corr_md = "\n".join(
        [f"| {a} | {b} | {v:.4f} |" for a, b, v in top_corrs[:12]]
    )

    date_section = ""
    if date_info:
        for col, info in date_info.items():
            date_section += (
                f"- **{col}**: min `{info['min']}`, max `{info['max']}`, "
                f"span `{info['span_days']}` days, non-null `{info['non_null']}`\n"
            )
    else:
        date_section = "- No reliably parseable date columns detected.\n"

    outlier_top = (
        outlier_df.sort_values("Outlier Percentage", ascending=False)
        .head(8)[["Column", "Outlier Count", "Outlier Percentage"]]
        .to_markdown(index=False)
        if not outlier_df.empty
        else "_No numeric outliers computed._"
    )

    miss_table = (
        miss_cols.head(15).to_markdown(index=False)
        if not miss_cols.empty
        else "_No missing values detected._"
    )

    cat_preview = cat_summary.head(15)[
        ["Column", "Unique Values", "Most Frequent", "Most Frequent Count"]
    ].to_markdown(index=False)

    report = f"""# SupplySight AI — Data Understanding Report

**Project:** SupplySight AI – Intelligent Supply Chain Analytics & Inventory Optimization Platform  
**Phase:** Data Understanding (EDA)  
**Date:** {date.today().isoformat()}  
**Analyst Role:** Senior Data Scientist / Senior Data Engineer  
**Scope:** Read-only profiling of raw DataCo Supply Chain datasets. No cleaning or modeling performed.

---

## 1. Executive Summary

The primary transactional dataset (`DataCoSupplyChainDataset.csv`) contains **{len(df):,} rows** and **{df.shape[1]} columns**, covering order-line commerce events with customer, product, shipping, geography, sales, and profit attributes.

A companion dictionary file (`DescriptionDataCoSupplyChain.csv`) documents **{len(desc):,} field descriptions**.

Key data-quality observations at a glance:

- **Missing values:** {len(miss_cols)} column(s) contain nulls (see Section 4).
- **Duplicate rows:** {int(dup_report.loc[0, 'Duplicate Rows']):,} ({dup_report.loc[0, 'Duplicate Percentage']}%).
- **Date fields detected:** {', '.join(date_cols) if date_cols else 'None'}.
- **Memory footprint (deep):** ~{mem_mb:.2f} MB.

This report establishes the factual baseline required before any cleaning, feature engineering, or ML work.

---

## 2. Dataset Overview

| Attribute | Value |
|-----------|-------|
| Main file | `data/raw/data/DataCoSupplyChainDataset.csv` |
| Description file | `data/raw/data/DescriptionDataCoSupplyChain.csv` |
| Rows | {len(df):,} |
| Columns | {df.shape[1]} |
| Memory (deep) | {mem_mb:.2f} MB |
| Encoding used | latin-1 |

### Column families present

| Domain | Present |
|--------|---------|
| Orders / order items | {"Yes" if has("Order Id", "Order Item Id", "Order Status") else "Partial"} |
| Customers | {"Yes" if has("Customer Id", "Customer Segment") else "Partial"} |
| Products / categories | {"Yes" if has("Product Name", "Category Name") else "Partial"} |
| Shipping / logistics | {"Yes" if has("Shipping Mode", "Delivery Status", "Days for shipping (real)") else "Partial"} |
| Sales / profit | {"Yes" if has("Sales", "Order Profit Per Order", "Benefit per order") else "Partial"} |
| Geography | {"Yes" if has("Order Country", "Customer City", "Market", "Order Region") else "Partial"} |
| Late delivery risk | {"Yes" if has("Late_delivery_risk") else "No"} |

Artifacts generated under `analysis/output/` include column, missing, duplicate, statistics, and categorical summaries.

---

## 3. Data Quality Assessment

| Check | Result |
|-------|--------|
| Schema consistency | {df.shape[1]} typed columns; mixed object/int/float |
| Completeness | {len(miss_cols)} columns with missing values |
| Uniqueness (full-row) | {dup_report.loc[0, 'Duplicate Percentage']}% duplicate rows |
| ID cardinality | Multiple identifier columns present (Customer Id, Order Id, Order Item Id, Product Card Id, etc.) |
| Sensitive fields | Customer Email / Password columns exist — treat as PII for future governance |
| Description coverage | Dictionary has {len(desc)} field docs vs {df.shape[1]} dataset columns |

**Overall quality posture:** Usable for analytics prototyping, but several completeness and governance issues must be addressed before production modeling or KPI dashboards.

---

## 4. Missing Values Summary

Columns with missing values (top 15 by count):

{miss_table}

Visualizations: `analysis/output/figures/missingno_matrix.png`, `missingno_bar.png`.  
CSV: `analysis/output/missing_values.csv`.

---

## 5. Duplicate Summary

| Metric | Value |
|--------|-------|
| Total rows | {int(dup_report.loc[0, 'Total Rows']):,} |
| Duplicate rows | {int(dup_report.loc[0, 'Duplicate Rows']):,} |
| Duplicate % | {dup_report.loc[0, 'Duplicate Percentage']} |
| Unique rows | {int(dup_report.loc[0, 'Unique Rows']):,} |

CSV: `analysis/output/duplicate_report.csv`.

---

## 6. Numerical Features Summary

Descriptive statistics were computed for all numeric columns and saved to `analysis/output/statistics.csv`.

### Outlier spotlight (IQR method, top columns)

{outlier_top}

Distribution and boxplot visuals: `numeric_histograms.png`, `numeric_boxplots.png`.

### Notable correlation pairs (absolute value)

| Feature A | Feature B | Correlation |
|-----------|-----------|-------------|
{top_corr_md}

Heatmap: `analysis/output/figures/correlation_heatmap.png`.

---

## 7. Categorical Features Summary

Object / categorical columns profiled in `analysis/output/categorical_summary.csv`.

Preview (top 15 columns by listing order):

{cat_preview}

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
{date_section}

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
"""
    (ANALYSIS / "Data_Understanding_Report.md").write_text(report, encoding="utf-8")


def build_notebook() -> None:
    """Create professional Jupyter notebook mirroring the analysis workflow."""
    import nbformat as nbf

    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }

    cells = []

    def md(text: str) -> None:
        cells.append(nbf.v4.new_markdown_cell(text))

    def code(text: str) -> None:
        cells.append(nbf.v4.new_code_cell(text))

    md(
        """# SupplySight AI — Data Understanding

**Phase:** Data Understanding / Exploratory Analysis  
**Objective:** Profile raw DataCo Supply Chain datasets for enterprise analytics readiness.

> **Guardrails:** This notebook does **not** clean data, rename columns, build dashboards, or train models. Analysis is read-only against raw CSVs.
"""
    )

    md("## 1. Environment & Libraries")
    code(
        """# Core analysis stack for enterprise data understanding
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import missingno as msno

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", context="notebook")
pd.set_option("display.max_columns", 100)
pd.set_option("display.max_rows", 100)

ROOT = Path("..") if Path("..", "data").exists() else Path(".")
# Prefer project-relative paths when notebook runs from analysis/
if not (ROOT / "data" / "raw" / "data" / "DataCoSupplyChainDataset.csv").exists():
    ROOT = Path(r"D:/Data Science Project/SupplySightAi")

RAW_MAIN = ROOT / "data" / "raw" / "data" / "DataCoSupplyChainDataset.csv"
RAW_DESC = ROOT / "data" / "raw" / "data" / "DescriptionDataCoSupplyChain.csv"
OUTPUT = Path("output") if Path("output").exists() or Path(".").resolve().name == "analysis" else ROOT / "analysis" / "output"
if not str(OUTPUT).endswith("output"):
    OUTPUT = ROOT / "analysis" / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)
(OUTPUT / "figures").mkdir(parents=True, exist_ok=True)

print("ROOT:", ROOT.resolve())
print("OUTPUT:", OUTPUT.resolve())
"""
    )

    md("## 2. Load Raw Datasets\n\nLoad both CSVs with `latin-1` encoding (DataCo standard). **No transformations.**")
    code(
        """# Load transactional supply-chain dataset and field dictionary
df = pd.read_csv(RAW_MAIN, encoding="latin-1", low_memory=False)
desc = pd.read_csv(RAW_DESC, encoding="latin-1")

print("Main dataset loaded:", df.shape)
print("Description dictionary loaded:", desc.shape)
desc.head(10)
"""
    )

    md("## 3. Dataset Overview")
    code(
        """# High-level shape, preview, schema, and memory footprint
print("Dataset Shape:", df.shape)
print("Number of Rows:", len(df))
print("Number of Columns:", df.shape[1])
print("\\nMemory Usage (deep): {:.2f} MB".format(df.memory_usage(deep=True).sum() / 1024**2))

print("\\n--- First 5 Rows ---")
display(df.head())

print("--- Last 5 Rows ---")
display(df.tail())

print("--- Column Names ---")
print(list(df.columns))

print("\\n--- Data Types ---")
display(df.dtypes.to_frame("dtype"))

print("--- Memory Usage by Column (top 15) ---")
display(df.memory_usage(deep=True).sort_values(ascending=False).head(15).to_frame("bytes"))
"""
    )

    md("## 4. Column Analysis\n\nBuild a column dictionary profile and persist to `output/column_summary.csv`.")
    code(
        """# Column-level profile: dtype, missingness, cardinality, example value
rows = []
for col in df.columns:
    s = df[col]
    non_null = s.dropna()
    missing = int(s.isna().sum())
    rows.append({
        "Column Name": col,
        "Data Type": str(s.dtype),
        "Missing Values": missing,
        "Missing Percentage": round(100.0 * missing / len(df), 4),
        "Unique Values": int(s.nunique(dropna=True)),
        "Example Value": non_null.iloc[0] if len(non_null) else np.nan,
    })

column_summary = pd.DataFrame(rows)
column_summary.to_csv(OUTPUT / "column_summary.csv", index=False)
display(column_summary)
"""
    )

    md("## 5. Missing Value Analysis")
    code(
        """# Missing value table + missingno visuals
missing_report = (
    pd.DataFrame({
        "Column": df.columns,
        "Missing Values": df.isna().sum().values,
        "Missing Percentage": np.round(100.0 * df.isna().sum().values / len(df), 4),
    })
    .sort_values("Missing Values", ascending=False)
    .reset_index(drop=True)
)
missing_report.to_csv(OUTPUT / "missing_values.csv", index=False)
display(missing_report[missing_report["Missing Values"] > 0])

miss_cols = df.columns[df.isna().any()].tolist()
sample = df if len(df) <= 5000 else df.sample(5000, random_state=42)
plot_df = sample[miss_cols] if miss_cols else sample.iloc[:, :20]

msno.matrix(plot_df, figsize=(14, 6), fontsize=9)
plt.title("Missing Value Matrix")
plt.show()

msno.bar(plot_df, figsize=(14, 6), fontsize=9)
plt.title("Missing Value Bars")
plt.show()
"""
    )

    md("## 6. Duplicate Analysis")
    code(
        """# Full-row duplicate assessment (no rows dropped)
dup_count = int(df.duplicated().sum())
duplicate_report = pd.DataFrame([{
    "Total Rows": len(df),
    "Duplicate Rows": dup_count,
    "Duplicate Percentage": round(100.0 * dup_count / len(df), 6),
    "Unique Rows": len(df) - dup_count,
}])
duplicate_report.to_csv(OUTPUT / "duplicate_report.csv", index=False)
display(duplicate_report)
"""
    )

    md("## 7. Numerical Analysis\n\nSummary statistics, distributions, boxplots, and IQR outlier profiling.")
    code(
        """# Numeric describe + plots + outlier table
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
statistics = df[numeric_cols].describe().T
statistics.to_csv(OUTPUT / "statistics.csv")
display(statistics)

# Prefer business metrics for readable plots
preferred = [
    "Days for shipping (real)", "Days for shipment (scheduled)", "Benefit per order",
    "Sales per customer", "Late_delivery_risk", "Order Item Discount",
    "Order Item Discount Rate", "Order Item Product Price", "Order Item Profit Ratio",
    "Order Item Quantity", "Sales", "Order Item Total", "Order Profit Per Order",
    "Product Price", "Product Status",
]
plot_cols = [c for c in preferred if c in df.columns]

fig, axes = plt.subplots(int(np.ceil(len(plot_cols)/3)), 3, figsize=(14, 3.2 * np.ceil(len(plot_cols)/3)))
axes = np.array(axes).reshape(-1)
for i, col in enumerate(plot_cols):
    axes[i].hist(df[col].dropna(), bins=40, color="#1f4e79", alpha=0.85)
    axes[i].set_title(col, fontsize=9)
for j in range(i+1, len(axes)):
    axes[j].axis("off")
fig.suptitle("Histograms — Key Numerical Features")
plt.tight_layout()
plt.show()

fig, axes = plt.subplots(int(np.ceil(len(plot_cols)/3)), 3, figsize=(14, 3.2 * np.ceil(len(plot_cols)/3)))
axes = np.array(axes).reshape(-1)
for i, col in enumerate(plot_cols):
    axes[i].boxplot(df[col].dropna(), vert=True)
    axes[i].set_title(col, fontsize=9)
for j in range(i+1, len(axes)):
    axes[j].axis("off")
fig.suptitle("Boxplots — Outlier View")
plt.tight_layout()
plt.show()

outlier_rows = []
for col in numeric_cols:
    s = df[col].dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = int(((s < lower) | (s > upper)).sum())
    outlier_rows.append({
        "Column": col, "Outlier Count": outliers,
        "Outlier Percentage": round(100.0 * outliers / len(s), 4),
        "Lower Bound": lower, "Upper Bound": upper,
    })
outlier_df = pd.DataFrame(outlier_rows).sort_values("Outlier Percentage", ascending=False)
display(outlier_df.head(15))
"""
    )

    md("## 8. Categorical Analysis")
    code(
        """# Categorical / object column frequency profiles
cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
# Include low-cardinality integer flags often used as categoricals
for col in ["Late_delivery_risk", "Product Status"]:
    if col in df.columns and col not in cat_cols:
        cat_cols.append(col)

cat_rows = []
for col in cat_cols:
    vc = df[col].value_counts(dropna=False).head(10)
    top_str = "; ".join([f"{idx} ({cnt})" for idx, cnt in vc.items()])
    cat_rows.append({
        "Column": col,
        "Unique Values": int(df[col].nunique(dropna=True)),
        "Top Categories (value count)": top_str,
        "Most Frequent": vc.index[0] if len(vc) else np.nan,
        "Most Frequent Count": int(vc.iloc[0]) if len(vc) else 0,
    })

categorical_summary = pd.DataFrame(cat_rows)
categorical_summary.to_csv(OUTPUT / "categorical_summary.csv", index=False)
display(categorical_summary)

# Interactive Plotly bar for a key business categorical
if "Delivery Status" in df.columns:
    status_counts = df["Delivery Status"].value_counts().reset_index()
    status_counts.columns = ["Delivery Status", "Count"]
    fig = px.bar(status_counts, x="Delivery Status", y="Count", title="Delivery Status Frequency")
    fig.show()
"""
    )

    md("## 9. Date Analysis\n\nAutomatically detect date-like columns and summarize timeline coverage.")
    code(
        """# Detect and profile date/datetime columns without mutating source df permanently
date_candidates = [c for c in df.columns if any(t in c.lower() for t in ("date", "time", "timestamp"))]
for col in df.select_dtypes(include="object").columns:
    if col in date_candidates:
        continue
    sample = df[col].dropna().astype(str).head(50)
    if sample.empty:
        continue
    parsed = pd.to_datetime(sample, errors="coerce")
    if parsed.notna().mean() >= 0.8:
        date_candidates.append(col)

print("Detected date columns:", date_candidates)
date_info = {}
for col in date_candidates:
    parsed = pd.to_datetime(df[col], errors="coerce")
    valid = parsed.dropna()
    if valid.empty:
        continue
    date_info[col] = {
        "min": valid.min(),
        "max": valid.max(),
        "span_days": (valid.max() - valid.min()).days,
        "non_null": int(valid.shape[0]),
        "nulls": int(parsed.isna().sum()),
    }
    print(f"\\n{col}: min={valid.min()} | max={valid.max()} | span_days={(valid.max()-valid.min()).days}")

# Timeline of record volume for primary order date if available
primary = "order date (DateOrders)" if "order date (DateOrders)" in df.columns else (date_candidates[0] if date_candidates else None)
if primary:
    parsed = pd.to_datetime(df[primary], errors="coerce")
    daily = parsed.dt.to_period("M").value_counts().sort_index()
    daily.index = daily.index.astype(str)
    fig = px.line(x=daily.index, y=daily.values, labels={"x": "Month", "y": "Records"}, title=f"Record Timeline — {primary}")
    fig.show()
"""
    )

    md("## 10. Correlation Analysis")
    code(
        """# Correlation matrix among business numeric measures (IDs excluded from heatmap focus)
exclude = {
    "customer id", "order id", "order item id", "order customer id", "product card id",
    "order item cardprod id", "category id", "department id", "product category id",
    "customer zipcode", "order zipcode",
}
corr_cols = [c for c in numeric_cols if c.lower() not in exclude]
corr = df[corr_cols].corr(numeric_only=True)
display(corr.round(3))

plt.figure(figsize=(14, 11))
sns.heatmap(corr, cmap="RdBu_r", center=0, square=True, linewidths=0.2, cbar_kws={"shrink": 0.7})
plt.title("Correlation Heatmap — Numerical Features")
plt.tight_layout()
plt.show()

# Highlight strongest absolute correlations
pairs = []
cols = corr.columns.tolist()
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        val = corr.iloc[i, j]
        if pd.notna(val):
            pairs.append((cols[i], cols[j], float(val)))
pairs.sort(key=lambda x: abs(x[2]), reverse=True)
print("Top absolute correlations:")
for a, b, v in pairs[:15]:
    print(f"  {a}  <->  {b}: {v:.4f}")
"""
    )

    md(
        """## 11. Business Understanding

### Orders
The dataset is primarily at **order-item grain** (`Order Id` + `Order Item Id`). Use this carefully when computing order-level KPIs.

### Customers
Customer identity and segmentation fields (`Customer Id`, `Customer Segment`, geography, contact fields) support cohort and segment analysis. Email/password are PII.

### Products & Categories
Product catalog attributes (`Product Name`, `Product Price`, `Category Name`, `Department Name`) enable assortment and pricing analytics.

### Shipping / Logistics
`Shipping Mode`, scheduled vs real shipping days, `Delivery Status`, and `Late_delivery_risk` are central to SLA and delay analytics.

### Sales & Profit
`Sales`, discounts, totals, benefit/profit fields support revenue and margin monitoring.

### Geography
Market, region, country, city, and coordinates enable regional performance and logistics views.

### Inventory
Explicit on-hand inventory is limited; future inventory optimization may require warehouse stock feeds beyond this extract.
"""
    )

    md("## 12. Export Confirmation\n\nAll tabular artifacts written under `analysis/output/`. Full narrative report: `analysis/Data_Understanding_Report.md`.")
    code(
        """# Confirm exports exist
for name in [
    "column_summary.csv",
    "missing_values.csv",
    "duplicate_report.csv",
    "statistics.csv",
    "categorical_summary.csv",
]:
    path = OUTPUT / name
    print(("[OK]" if path.exists() else "[MISSING]"), path)
"""
    )

    nb.cells = cells
    nbf.write(nb, ANALYSIS / "01_data_understanding.ipynb")


def main() -> None:
    print("Loading data...")
    df, desc = load_data()
    print(f"Loaded main={df.shape}, desc={desc.shape}")

    print("Column summary...")
    col_summary = build_column_summary(df)
    col_summary.to_csv(OUTPUT / "column_summary.csv", index=False)

    print("Missing analysis...")
    missing_report = missing_analysis(df)
    missing_report.to_csv(OUTPUT / "missing_values.csv", index=False)
    save_missing_plot(df)

    print("Duplicate analysis...")
    dup_report = duplicate_analysis(df)
    dup_report.to_csv(OUTPUT / "duplicate_report.csv", index=False)

    print("Numerical analysis...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats = df[numeric_cols].describe().T
    stats.to_csv(OUTPUT / "statistics.csv")
    outlier_df = outlier_summary(df, numeric_cols)
    outlier_df.to_csv(OUTPUT / "outlier_summary.csv", index=False)
    save_numeric_plots(df, numeric_cols)

    print("Categorical analysis...")
    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    for col in ["Late_delivery_risk", "Product Status"]:
        if col in df.columns and col not in cat_cols:
            cat_cols.append(col)
    cat_summary = categorical_summary(df, cat_cols)
    cat_summary.to_csv(OUTPUT / "categorical_summary.csv", index=False)

    print("Date analysis...")
    date_cols = detect_datetime_columns(df)
    date_info = {}
    for col in date_cols:
        parsed = pd.to_datetime(df[col], errors="coerce")
        valid = parsed.dropna()
        if valid.empty:
            continue
        date_info[col] = {
            "min": valid.min(),
            "max": valid.max(),
            "span_days": (valid.max() - valid.min()).days,
            "non_null": int(valid.shape[0]),
        }
        # Timeline plot for order date
        if "order date" in col.lower() or col == date_cols[0]:
            monthly = parsed.dt.to_period("M").value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(range(len(monthly)), monthly.values, color="#1f4e79")
            ax.set_xticks(range(0, len(monthly), max(1, len(monthly) // 12)))
            ax.set_xticklabels(
                [str(x) for x in monthly.index[:: max(1, len(monthly) // 12)]],
                rotation=45,
                ha="right",
                fontsize=8,
            )
            ax.set_title(f"Record Timeline — {col}")
            ax.set_ylabel("Records")
            fig.tight_layout()
            fig.savefig(FIGURES / "record_timeline.png")
            plt.close(fig)

    print("Correlation analysis...")
    _, top_corrs = save_correlation(df, numeric_cols)

    print("Writing markdown report...")
    write_report(
        df,
        desc,
        col_summary,
        missing_report,
        dup_report,
        stats,
        cat_summary,
        date_cols,
        date_info,
        outlier_df,
        top_corrs,
    )

    print("Building notebook...")
    build_notebook()

    print("Done.")
    print("Outputs:", OUTPUT)
    print("Report:", ANALYSIS / "Data_Understanding_Report.md")
    print("Notebook:", ANALYSIS / "01_data_understanding.ipynb")


if __name__ == "__main__":
    main()
