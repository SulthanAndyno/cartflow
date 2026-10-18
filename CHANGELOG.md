# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/).

## [0.1.0] - 2026-10-18

### Ditambahkan
- Pipeline extract, transform, load dari dataset Olist ke DuckDB.
- Star schema dengan tabel fact_sales, dim_customer, dim_product, dan dim_date.
- View mart penjualan bulanan, kategori teratas, dan pelanggan per negara bagian, beserta ekspor CSV.
- Pseudonimisasi customer_unique_id dengan hash SHA-256 bersalt.
- Delapan pengecekan kualitas data dengan log hasil per eksekusi.
- Workflow CI untuk lint dan test, serta workflow pipeline harian.
- Ringkasan operasional di halaman run GitHub Actions.
- Data dictionary dan runbook.
- Kolom month_start pada mart_sales_monthly untuk sumbu waktu dashboard.
- Dashboard Data Studio.
