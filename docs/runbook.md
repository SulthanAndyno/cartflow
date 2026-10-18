# Runbook

Panduan penanganan ketika pipeline gagal. Langkah pertama selalu sama: buka run yang gagal di tab Actions, lihat langkah mana yang merah, lalu baca log dan ringkasan run.

## Extract gagal karena autentikasi Kaggle

Gejala: langkah `python -m pipeline` berhenti saat extract dengan pesan 401 atau 403 dari Kaggle.

Penyebab yang umum adalah secret `KAGGLE_USERNAME` atau `KAGGLE_KEY` belum diisi, salah ketik, atau API token sudah dicabut.

Penanganan:
1. Buat API token baru di halaman Settings akun Kaggle.
2. Perbarui kedua secret di Settings > Secrets and variables > Actions.
3. Jalankan ulang workflow lewat tombol Run workflow.

## Extract gagal karena file tidak ditemukan

Gejala: `FileNotFoundError` untuk salah satu file CSV.

Penyebab yang umum adalah pemilik dataset mengganti nama atau menghapus file pada versi baru.

Penanganan:
1. Cek daftar file pada versi terbaru dataset di halaman Kaggle.
2. Sesuaikan daftar `TABLES` di `pipeline/extract.py`.
3. Jika struktur kolom ikut berubah, lanjutkan ke bagian perubahan skema.

## Transform gagal karena perubahan skema

Gejala: `KeyError` dengan nama kolom pada `pipeline/transform.py`, atau error kolom tidak dikenal pada `sql/star_schema.sql`.

Penanganan:
1. Unduh data mentah di lokal dengan `uv run python -c "from pipeline.extract import extract; extract()"`, lalu bandingkan header CSV dengan kolom yang dipakai kode.
2. Sesuaikan transform dan SQL, lalu tambahkan atau perbarui test di `tests/test_pipeline.py`.
3. Ajukan perubahan lewat pull request dan catat di `CHANGELOG.md`.

## Cek kualitas gagal

Gejala: pipeline keluar dengan kode 1 dan log berisi `cek kualitas gagal: <nama cek>`. Mart tidak diekspor sehingga dashboard tetap memakai data lama yang valid.

Penanganan:
1. Lihat jumlah baris bermasalah pada `quality_log.csv` di artifact run.
2. Cari baris penyebabnya di lokal. Contoh untuk cek harga:
   ```sql
   SELECT * FROM fact_sales WHERE price <= 0;
   ```
3. Tentukan apakah masalahnya ada di data sumber atau di kode transform.
   - Jika di kode, perbaiki transform dan tambahkan test yang menangkap kasus tersebut.
   - Jika di data sumber dan barisnya memang tidak valid, tambahkan aturan pembersihan di transform dan dokumentasikan alasannya di README bagian Pembersihan data.
4. Jangan menghapus atau melonggarkan cek hanya agar pipeline lolos.

## Pipeline melebihi batas waktu

Gejala: run dibatalkan setelah 20 menit.

Penanganan:
1. Cek apakah unduhan dari Kaggle lambat dengan melihat durasi langkah extract di log.
2. Jalankan ulang workflow. Jika berulang, naikkan `timeout-minutes` di `pipeline.yml` dan catat alasannya di `CHANGELOG.md`.
