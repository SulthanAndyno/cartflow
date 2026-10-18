# Data Dictionary

Klasifikasi data memakai tiga tingkat. Publik berarti aman ditampilkan di dashboard. Internal berarti pengenal teknis yang tidak terkait langsung dengan orang. Pribadi berarti data yang dapat dikaitkan dengan individu dan wajib dilindungi.

## fact_sales

Satu baris per item dalam pesanan.

| Kolom | Tipe | Deskripsi | Klasifikasi |
|---|---|---|---|
| order_id | VARCHAR | ID pesanan. Bagian kunci utama bersama order_item_id | Internal |
| order_item_id | BIGINT | Nomor urut item dalam satu pesanan, mulai dari 1 | Internal |
| customer_id | VARCHAR | ID pelanggan per pesanan, merujuk ke dim_customer | Internal |
| product_id | VARCHAR | ID produk, merujuk ke dim_product | Internal |
| date_key | INTEGER | Tanggal pembelian dalam format YYYYMMDD, merujuk ke dim_date | Publik |
| seller_id | VARCHAR | ID penjual | Internal |
| order_status | VARCHAR | Status pesanan dalam huruf kecil: delivered, shipped, canceled, invoiced, processing, unavailable, approved | Publik |
| price | DOUBLE | Harga item dalam BRL, selalu lebih dari nol | Publik |
| freight_value | DOUBLE | Ongkos kirim item dalam BRL, tidak negatif | Publik |
| total_value | DOUBLE | price ditambah freight_value | Publik |

## dim_customer

Satu baris per customer_id. Satu pelanggan dapat memiliki beberapa customer_id karena Olist membuat ID baru di setiap pesanan.

| Kolom | Tipe | Deskripsi | Klasifikasi |
|---|---|---|---|
| customer_id | VARCHAR | ID pelanggan per pesanan, kunci utama | Internal |
| customer_uid_hash | VARCHAR | Hash SHA-256 bersalt (16 karakter) dari customer_unique_id. Dipakai untuk menghitung pelanggan unik | Pribadi (dipseudonimisasi) |
| customer_city | VARCHAR | Nama kota dengan huruf kapital di awal kata | Publik |
| customer_state | VARCHAR | Kode negara bagian Brasil, dua huruf kapital | Publik |

Kolom sumber yang sengaja tidak dibawa ke warehouse: `customer_unique_id` (pengenal pelanggan asli) dan `customer_zip_code_prefix` (kode pos, tidak dibutuhkan untuk analisis).

## dim_product

| Kolom | Tipe | Deskripsi | Klasifikasi |
|---|---|---|---|
| product_id | VARCHAR | ID produk, kunci utama | Internal |
| category | VARCHAR | Kategori produk dalam bahasa Inggris. Bernilai `unknown` jika kategori kosong atau tidak ada di tabel terjemahan | Publik |
| product_weight_g | DOUBLE | Berat produk dalam gram, dapat null | Publik |
| product_photos_qty | DOUBLE | Jumlah foto produk, dapat null | Publik |

## dim_date

Satu baris per tanggal, dari tanggal pembelian paling awal sampai paling akhir.

| Kolom | Tipe | Deskripsi | Klasifikasi |
|---|---|---|---|
| date_key | INTEGER | Tanggal dalam format YYYYMMDD, kunci utama | Publik |
| date | DATE | Tanggal | Publik |
| year | BIGINT | Tahun | Publik |
| month | BIGINT | Bulan, 1 sampai 12 | Publik |
| quarter | BIGINT | Kuartal, 1 sampai 4 | Publik |
| day_of_week | BIGINT | Hari dalam minggu, 0 untuk Minggu sampai 6 untuk Sabtu | Publik |

## Mart

| View | Isi |
|---|---|
| mart_sales_monthly | month_start (tanggal 1 tiap bulan), year, month, jumlah pesanan unik, dan pendapatan (jumlah price) per bulan, tanpa pesanan canceled dan unavailable |
| mart_top_categories | category, jumlah item terjual, dan pendapatan per kategori, tanpa pesanan canceled dan unavailable |
| mart_customers_by_state | customer_state dan jumlah pelanggan unik berdasarkan customer_uid_hash |
