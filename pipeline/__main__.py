"""Jalankan seluruh pipeline: python -m pipeline"""

import logging
import os
import sys

from pipeline.extract import extract
from pipeline.load import export_marts, load
from pipeline.quality import run_checks
from pipeline.transform import transform

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("pipeline")

TABLES = ["fact_sales", "dim_customer", "dim_product", "dim_date"]


def write_summary(con, failed: list[str]) -> None:
    """Tulis ringkasan operasional ke halaman run GitHub Actions (hanya saat berjalan di Actions)."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    lines = ["## Ringkasan pipeline", "", "| Tabel | Jumlah baris |", "|---|---|"]
    lines += [f"| {t} | {con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]:,} |" for t in TABLES]
    lines += ["", f"Cek kualitas gagal: {len(failed)}"] + [f"- {name}" for name in failed]
    with open(path, "a") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    raw = extract()
    log.info("extract selesai: %s", raw)
    tables = transform(raw)
    for name, df in tables.items():
        log.info("transform %s: %d baris", name, len(df))
    con = load(tables)
    log.info("fact_sales: %d baris", con.execute("SELECT count(*) FROM fact_sales").fetchone()[0])
    failed = run_checks(con)
    write_summary(con, failed)
    if failed:
        for name in failed:
            log.error("cek kualitas gagal: %s", name)
        return 1
    export_marts(con)
    log.info("semua cek kualitas lolos, mart diekspor ke data/export")
    return 0


if __name__ == "__main__":
    sys.exit(main())
