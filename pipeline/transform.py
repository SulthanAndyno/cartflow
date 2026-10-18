"""Transform: membersihkan tabel mentah sebelum dimuat ke warehouse."""

import hashlib
import os
from pathlib import Path

import pandas as pd

ORDER_DATES = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def pseudonymize(value: str, salt: str) -> str:
    """Ganti ID pelanggan asli dengan hash SHA-256 bersalt (pseudonimisasi data pribadi)."""
    return hashlib.sha256((salt + value).encode()).hexdigest()[:16]


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates("order_id").copy()
    for col in ORDER_DATES:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["order_status"] = df["order_status"].str.strip().str.lower()
    return df


def clean_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(["order_id", "order_item_id"]).copy()
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
    return df


def clean_customers(df: pd.DataFrame, salt: str) -> pd.DataFrame:
    df = df.drop_duplicates("customer_id").copy()
    df["customer_uid_hash"] = df["customer_unique_id"].map(lambda v: pseudonymize(v, salt))
    df["customer_city"] = df["customer_city"].str.strip().str.title()
    df["customer_state"] = df["customer_state"].str.strip().str.upper()
    # ID asli dan kode pos tidak dibawa ke warehouse
    return df[["customer_id", "customer_uid_hash", "customer_city", "customer_state"]]


def clean_products(df: pd.DataFrame, translation: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates("product_id").merge(translation, on="product_category_name", how="left")
    df["category"] = df["product_category_name_english"].fillna("unknown")
    return df[["product_id", "category", "product_weight_g", "product_photos_qty"]]


def transform(raw: Path) -> dict[str, pd.DataFrame]:
    salt = os.environ.get("PII_SALT", "dev-salt")
    read = lambda name: pd.read_csv(raw / f"{name}.csv")
    return {
        "orders": clean_orders(read("olist_orders_dataset")),
        "items": clean_items(read("olist_order_items_dataset")),
        "customers": clean_customers(read("olist_customers_dataset"), salt),
        "products": clean_products(read("olist_products_dataset"), read("product_category_name_translation")),
    }
