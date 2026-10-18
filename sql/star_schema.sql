-- Star schema: satu fact (per item pesanan) dan tiga dimension.
-- Tabel stg_* dibuat dari hasil transform di Python.

CREATE OR REPLACE TABLE dim_customer AS
SELECT customer_id, customer_uid_hash, customer_city, customer_state
FROM stg_customers;

CREATE OR REPLACE TABLE dim_product AS
SELECT product_id, category, product_weight_g, product_photos_qty
FROM stg_products;

CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER) AS date_key,
    CAST(d AS DATE) AS date,
    year(d) AS year,
    month(d) AS month,
    quarter(d) AS quarter,
    dayofweek(d) AS day_of_week
FROM generate_series(
    (SELECT CAST(min(order_purchase_timestamp) AS DATE) FROM stg_orders),
    (SELECT CAST(max(order_purchase_timestamp) AS DATE) FROM stg_orders),
    INTERVAL 1 DAY
) AS t(d);

CREATE OR REPLACE TABLE fact_sales AS
SELECT
    i.order_id,
    i.order_item_id,
    o.customer_id,
    i.product_id,
    i.seller_id,
    CAST(strftime(o.order_purchase_timestamp, '%Y%m%d') AS INTEGER) AS date_key,
    o.order_status,
    i.price,
    i.freight_value,
    i.price + i.freight_value AS total_value
FROM stg_items i
JOIN stg_orders o USING (order_id);

-- Mart ringkas untuk dashboard
CREATE OR REPLACE VIEW mart_sales_monthly AS
SELECT make_date(d.year, d.month, 1) AS month_start, d.year, d.month, count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS revenue
FROM fact_sales f JOIN dim_date d USING (date_key)
WHERE f.order_status NOT IN ('canceled', 'unavailable')
GROUP BY ALL ORDER BY month_start;

CREATE OR REPLACE VIEW mart_top_categories AS
SELECT p.category, count(*) AS items_sold, round(sum(f.price), 2) AS revenue
FROM fact_sales f JOIN dim_product p USING (product_id)
WHERE f.order_status NOT IN ('canceled', 'unavailable')
GROUP BY ALL ORDER BY revenue DESC;

CREATE OR REPLACE VIEW mart_customers_by_state AS
SELECT customer_state, count(DISTINCT customer_uid_hash) AS customers
FROM dim_customer
GROUP BY ALL ORDER BY customers DESC;
