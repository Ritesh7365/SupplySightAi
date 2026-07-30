"""
SupplySight AI — DataCo → Normalized CSV ETL (no PostgreSQL writes).

Reads the flat DataCo supply-chain extract, splits it into relational tables,
deduplicates dimensions, preserves order-item relationships, and exports CSVs
to database/seed/.

Does NOT fabricate warehouse / inventory / vendor business rows.
Does NOT clean beyond dimension deduplication required for normalization.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / "data" / "raw" / "data" / "DataCoSupplyChainDataset.csv"
SEED_DIR = ROOT / "database" / "seed"


def load_source() -> pd.DataFrame:
    """Load raw DataCo CSV (latin-1). No column renames on the source frame."""
    print(f"Loading: {RAW_CSV}")
    df = pd.read_csv(RAW_CSV, encoding="latin-1", low_memory=False)
    print(f"Loaded rows={len(df):,} cols={df.shape[1]}")
    return df


def build_departments(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate department dimension."""
    out = (
        df[["Department Id", "Department Name"]]
        .drop_duplicates(subset=["Department Id"])
        .rename(
            columns={
                "Department Id": "department_id",
                "Department Name": "department_name",
            }
        )
        .sort_values("department_id")
        .reset_index(drop=True)
    )
    return out


def build_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate categories; attach department_id (1:1 in source)."""
    out = (
        df[["Category Id", "Category Name", "Department Id"]]
        .drop_duplicates(subset=["Category Id"])
        .rename(
            columns={
                "Category Id": "category_id",
                "Category Name": "category_name",
                "Department Id": "department_id",
            }
        )
        .sort_values("category_id")
        .reset_index(drop=True)
    )
    return out


def build_products(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate product catalog on Product Card Id."""
    cols = [
        "Product Card Id",
        "Product Name",
        "Product Category Id",
        "Product Price",
        "Product Status",
        "Product Description",
        "Product Image",
    ]
    out = (
        df[cols]
        .drop_duplicates(subset=["Product Card Id"])
        .rename(
            columns={
                "Product Card Id": "product_id",
                "Product Name": "product_name",
                "Product Category Id": "category_id",
                "Product Price": "product_price",
                "Product Status": "product_status",
                "Product Description": "product_description",
                "Product Image": "product_image_url",
            }
        )
        .sort_values("product_id")
        .reset_index(drop=True)
    )
    return out


def build_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate customers on Customer Id."""
    cols = [
        "Customer Id",
        "Customer Fname",
        "Customer Lname",
        "Customer Email",
        "Customer Password",
        "Customer Segment",
        "Customer Street",
        "Customer City",
        "Customer State",
        "Customer Zipcode",
        "Customer Country",
        "Latitude",
        "Longitude",
    ]
    out = (
        df[cols]
        .drop_duplicates(subset=["Customer Id"])
        .rename(
            columns={
                "Customer Id": "customer_id",
                "Customer Fname": "first_name",
                "Customer Lname": "last_name",
                "Customer Email": "email",
                "Customer Password": "password_mask",
                "Customer Segment": "customer_segment",
                "Customer Street": "street",
                "Customer City": "city",
                "Customer State": "state_code",
                "Customer Zipcode": "zipcode",
                "Customer Country": "country",
                "Latitude": "latitude",
                "Longitude": "longitude",
            }
        )
        .sort_values("customer_id")
        .reset_index(drop=True)
    )
    def _zip_to_str(value: object) -> object:
        if pd.isna(value):
            return pd.NA
        try:
            as_float = float(value)
            if as_float.is_integer():
                return str(int(as_float))
        except (TypeError, ValueError):
            pass
        return str(value)

    out["zipcode"] = out["zipcode"].map(_zip_to_str)
    return out


def build_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate order headers on Order Id.
    Uses first row per order for attributes validated as order-stable
    (status, geo, dates, type, market, customer).
    """
    order_cols = [
        "Order Id",
        "Order Customer Id",
        "order date (DateOrders)",
        "Order Status",
        "Type",
        "Market",
        "Order City",
        "Order State",
        "Order Country",
        "Order Region",
        "Order Zipcode",
    ]
    # Stable attributes: take first occurrence per Order Id
    out = (
        df[order_cols]
        .drop_duplicates(subset=["Order Id"], keep="first")
        .rename(
            columns={
                "Order Id": "order_id",
                "Order Customer Id": "customer_id",
                "order date (DateOrders)": "order_date",
                "Order Status": "order_status",
                "Type": "transaction_type",
                "Market": "market",
                "Order City": "order_city",
                "Order State": "order_state",
                "Order Country": "order_country",
                "Order Region": "order_region",
                "Order Zipcode": "order_zipcode",
            }
        )
        .sort_values("order_id")
        .reset_index(drop=True)
    )
    out["order_date"] = pd.to_datetime(out["order_date"], errors="coerce")
    out["order_zipcode"] = out["order_zipcode"].apply(
        lambda x: pd.NA
        if pd.isna(x)
        else str(int(x))
        if float(x).is_integer()
        else str(x)
    )
    return out


def build_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Full fact grain — one row per Order Item Id (no dedupe of facts)."""
    cols = [
        "Order Item Id",
        "Order Id",
        "Order Item Cardprod Id",
        "Order Item Quantity",
        "Order Item Product Price",
        "Order Item Discount",
        "Order Item Discount Rate",
        "Sales",
        "Order Item Total",
        "Order Item Profit Ratio",
        "Benefit per order",
        "Order Profit Per Order",
        "Sales per customer",
    ]
    out = (
        df[cols]
        .rename(
            columns={
                "Order Item Id": "order_item_id",
                "Order Id": "order_id",
                "Order Item Cardprod Id": "product_id",
                "Order Item Quantity": "quantity",
                "Order Item Product Price": "unit_price",
                "Order Item Discount": "discount_amount",
                "Order Item Discount Rate": "discount_rate",
                "Sales": "sales",
                "Order Item Total": "order_item_total",
                "Order Item Profit Ratio": "profit_ratio",
                "Benefit per order": "benefit_amount",
                "Order Profit Per Order": "profit_amount",
                "Sales per customer": "sales_per_customer",
            }
        )
        .sort_values("order_item_id")
        .reset_index(drop=True)
    )
    return out


def build_shipments(df: pd.DataFrame) -> pd.DataFrame:
    """One shipment profile per Order Id (matches source cardinality)."""
    cols = [
        "Order Id",
        "Shipping Mode",
        "shipping date (DateOrders)",
        "Delivery Status",
        "Late_delivery_risk",
        "Days for shipping (real)",
        "Days for shipment (scheduled)",
    ]
    out = (
        df[cols]
        .drop_duplicates(subset=["Order Id"], keep="first")
        .rename(
            columns={
                "Order Id": "order_id",
                "Shipping Mode": "shipping_mode",
                "shipping date (DateOrders)": "shipping_date",
                "Delivery Status": "delivery_status",
                "Late_delivery_risk": "late_delivery_risk",
                "Days for shipping (real)": "days_for_shipping_real",
                "Days for shipment (scheduled)": "days_for_shipment_scheduled",
            }
        )
        .sort_values("order_id")
        .reset_index(drop=True)
    )
    out["shipping_date"] = pd.to_datetime(out["shipping_date"], errors="coerce")
    # Surrogate shipment_id for CSV parity with schema (1..N)
    out.insert(0, "shipment_id", range(1, len(out) + 1))
    return out


def validate_relationships(
    departments: pd.DataFrame,
    categories: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    shipments: pd.DataFrame,
) -> None:
    """Integrity checks before export (fail loud on orphans)."""
    assert categories["department_id"].isin(departments["department_id"]).all()
    assert products["category_id"].isin(categories["category_id"]).all()
    assert orders["customer_id"].isin(customers["customer_id"]).all()
    assert order_items["order_id"].isin(orders["order_id"]).all()
    assert order_items["product_id"].isin(products["product_id"]).all()
    assert shipments["order_id"].isin(orders["order_id"]).all()
    assert shipments["order_id"].is_unique
    assert order_items["order_item_id"].is_unique
    assert len(order_items) > 0
    print("Relationship validation: OK")


def export_csv(df: pd.DataFrame, name: str) -> None:
    """Write UTF-8 CSV into seed directory."""
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    path = SEED_DIR / name
    df.to_csv(path, index=False)
    print(f"Wrote {path.name:20s} rows={len(df):>8,} cols={df.shape[1]}")


def main() -> None:
    df = load_source()

    departments = build_departments(df)
    categories = build_categories(df)
    products = build_products(df)
    customers = build_customers(df)
    orders = build_orders(df)
    order_items = build_order_items(df)
    shipments = build_shipments(df)

    validate_relationships(
        departments, categories, products, customers, orders, order_items, shipments
    )

    export_csv(departments, "departments.csv")
    export_csv(categories, "categories.csv")
    export_csv(products, "products.csv")
    export_csv(customers, "customers.csv")
    export_csv(orders, "orders.csv")
    export_csv(order_items, "order_items.csv")
    export_csv(shipments, "shipments.csv")

    print("\nETL complete. Placeholder tables (warehouses/inventory/vendors) not exported.")
    print(f"Seed directory: {SEED_DIR}")


if __name__ == "__main__":
    main()
