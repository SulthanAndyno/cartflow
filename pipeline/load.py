"""Load: muat hasil transform ke DuckDB dan bangun star schema."""

from pathlib import Path

import duckdb
import pandas as pd

WAREHOUSE = Path("data/warehouse.duckdb")
EXPORT = Path("data/export")
SCHEMA_SQL = Path(__file__).parent.parent / "sql" / "star_schema.sql"
MARTS = ["mart_sales_monthly", "mart_top_categories", "mart_customers_by_state"]


def load(tables: dict[str, pd.DataFrame], db_path: Path | str = WAREHOUSE) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(db_path))
    for name, df in tables.items():
        con.register("tmp", df)
        con.execute(f"CREATE OR REPLACE TABLE stg_{name} AS SELECT * FROM tmp")
        con.unregister("tmp")
    con.execute(SCHEMA_SQL.read_text())
    return con


def export_marts(con: duckdb.DuckDBPyConnection, out: Path = EXPORT) -> None:
    """Ekspor mart ke CSV supaya bisa diunggah ke Looker Studio."""
    out.mkdir(parents=True, exist_ok=True)
    for m in MARTS:
        con.execute(f"COPY {m} TO '{out / m}.csv' (HEADER)")
