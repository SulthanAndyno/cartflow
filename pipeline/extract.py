"""Extract: unduh dataset Olist dari Kaggle lalu salin tabel yang dipakai ke data/raw."""

import shutil
from pathlib import Path

DATASET = "olistbr/brazilian-ecommerce"
TABLES = [
    "olist_orders_dataset",
    "olist_order_items_dataset",
    "olist_customers_dataset",
    "olist_products_dataset",
    "product_category_name_translation",
]
RAW = Path("data/raw")


def extract() -> Path:
    import kagglehub

    src = Path(kagglehub.dataset_download(DATASET))
    RAW.mkdir(parents=True, exist_ok=True)
    for t in TABLES:
        shutil.copy(src / f"{t}.csv", RAW / f"{t}.csv")
    return RAW
