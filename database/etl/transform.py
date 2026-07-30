"""
SupplySight AI — ETL Transform stage.

Structurally normalizes the flat DataCo extract into relational DataFrames.
Deduplicates dimensions only; preserves all transactional order-item rows.
Does not clean or alter business measure values.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from utils import frame_summary, zipcode_to_str

logger = logging.getLogger("supplysight.etl.transform")


@dataclass
class TransformResult:
    """Normalized relational frames ready for CSV load."""

    departments: pd.DataFrame
    categories: pd.DataFrame
    products: pd.DataFrame
    customers: pd.DataFrame
    orders: pd.DataFrame
    order_items: pd.DataFrame
    shipments: pd.DataFrame


class TransformError(Exception):
    """Raised when normalization or FK validation fails."""


def _build_departments(df: pd.DataFrame) -> pd.DataFrame:
    """Build deduplicated departments dimension."""
    return (
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


def _build_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Build deduplicated categories with department FK."""
    return (
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


def _build_products(df: pd.DataFrame) -> pd.DataFrame:
    """Build deduplicated products catalog."""
    cols = [
        "Product Card Id",
        "Product Name",
        "Product Category Id",
        "Product Price",
        "Product Status",
        "Product Description",
        "Product Image",
    ]
    return (
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


def _build_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Build deduplicated customers dimension."""
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
    # Structural cast for zipcode storage only (values unchanged semantically)
    out["zipcode"] = out["zipcode"].map(zipcode_to_str)
    return out


def _build_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Build order headers (one row per Order Id)."""
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
    # Parse timestamp representation for schema alignment (values preserved)
    out["order_date"] = pd.to_datetime(out["order_date"], errors="coerce")
    out["order_zipcode"] = out["order_zipcode"].map(zipcode_to_str)
    return out


def _build_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Build full order-item fact table — no transactional rows removed."""
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
    return (
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


def _build_shipments(df: pd.DataFrame) -> pd.DataFrame:
    """Build one shipment profile per order (matches DataCo cardinality)."""
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
    out.insert(0, "shipment_id", range(1, len(out) + 1))
    return out


def validate_foreign_keys(result: TransformResult, source_row_count: int) -> None:
    """
    Ensure normalized FKs resolve and transactional grain is preserved.

    Raises
    ------
    TransformError
        On orphan keys or lost order-item rows.
    """
    logger.info("Validating foreign keys and grain preservation...")

    checks = [
        (
            "categories.department_id -> departments",
            result.categories["department_id"].isin(
                result.departments["department_id"]
            ).all(),
        ),
        (
            "products.category_id -> categories",
            result.products["category_id"].isin(result.categories["category_id"]).all(),
        ),
        (
            "orders.customer_id -> customers",
            result.orders["customer_id"].isin(result.customers["customer_id"]).all(),
        ),
        (
            "order_items.order_id -> orders",
            result.order_items["order_id"].isin(result.orders["order_id"]).all(),
        ),
        (
            "order_items.product_id -> products",
            result.order_items["product_id"].isin(result.products["product_id"]).all(),
        ),
        (
            "shipments.order_id -> orders",
            result.shipments["order_id"].isin(result.orders["order_id"]).all(),
        ),
        ("shipments.order_id unique", bool(result.shipments["order_id"].is_unique)),
        (
            "order_items.order_item_id unique",
            bool(result.order_items["order_item_id"].is_unique),
        ),
        (
            "order_items row count preserved",
            len(result.order_items) == source_row_count,
        ),
    ]

    failures = [name for name, ok in checks if not ok]
    if failures:
        raise TransformError("FK/grain validation failed: " + "; ".join(failures))

    logger.info("Foreign key validation passed (%s checks)", len(checks))


def transform(raw_df: pd.DataFrame) -> TransformResult:
    """
    Split the flat extract into normalized relational DataFrames.

    Parameters
    ----------
    raw_df:
        Untouched DataCo dataframe from extract.

    Returns
    -------
    TransformResult
        Dimension + fact frames aligned to PostgreSQL schema column names.
    """
    logger.info("Starting transform (source rows=%s)", f"{len(raw_df):,}")

    result = TransformResult(
        departments=_build_departments(raw_df),
        categories=_build_categories(raw_df),
        products=_build_products(raw_df),
        customers=_build_customers(raw_df),
        orders=_build_orders(raw_df),
        order_items=_build_order_items(raw_df),
        shipments=_build_shipments(raw_df),
    )

    for name, frame in (
        ("departments", result.departments),
        ("categories", result.categories),
        ("products", result.products),
        ("customers", result.customers),
        ("orders", result.orders),
        ("order_items", result.order_items),
        ("shipments", result.shipments),
    ):
        logger.info("Built %s", frame_summary(name, frame))

    validate_foreign_keys(result, source_row_count=len(raw_df))
    logger.info("Transform complete")
    return result
