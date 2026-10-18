"""Cek kualitas data pada warehouse. Tiap cek berupa query yang menghitung baris bermasalah."""

import csv
from datetime import UTC, datetime
from pathlib import Path

import duckdb

LOG = Path("data/quality_log.csv")

CHECKS = {
    "fact_sales: price tidak boleh negatif atau nol": "SELECT count(*) FROM fact_sales WHERE price <= 0",
    "fact_sales: freight tidak boleh negatif": "SELECT count(*) FROM fact_sales WHERE freight_value < 0",
    "fact_sales: item pesanan tidak boleh duplikat": """
        SELECT count(*) FROM (
            SELECT order_id, order_item_id FROM fact_sales GROUP BY ALL HAVING count(*) > 1
        )""",
    "fact_sales: date_key harus ada di dim_date": """
        SELECT count(*) FROM fact_sales f LEFT JOIN dim_date d USING (date_key) WHERE d.date_key IS NULL""",
    "fact_sales: customer harus ada di dim_customer": """
        SELECT count(*) FROM fact_sales f LEFT JOIN dim_customer c USING (customer_id)
        WHERE c.customer_id IS NULL""",
    "fact_sales: product harus ada di dim_product": """
        SELECT count(*) FROM fact_sales f LEFT JOIN dim_product p USING (product_id)
        WHERE p.product_id IS NULL""",
    "dim_customer: customer_id tidak boleh null": "SELECT count(*) FROM dim_customer WHERE customer_id IS NULL",
    "dim_customer: tidak ada kolom ID pelanggan asli": """
        SELECT count(*) FROM information_schema.columns
        WHERE table_name = 'dim_customer' AND column_name = 'customer_unique_id'""",
}


def run_checks(con: duckdb.DuckDBPyConnection, log: Path = LOG) -> list[str]:
    """Jalankan semua cek, tulis hasilnya ke log, dan kembalikan nama cek yang gagal."""
    now = datetime.now(UTC).isoformat(timespec="seconds")
    rows = [(now, name, con.execute(sql).fetchone()[0]) for name, sql in CHECKS.items()]
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    with log.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["run_at", "check", "failed_rows"])
        w.writerows(rows)
    return [name for _, name, bad in rows if bad > 0]
