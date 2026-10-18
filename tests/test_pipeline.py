import pandas as pd

from pipeline.load import load
from pipeline.quality import run_checks
from pipeline.transform import clean_customers, clean_items, clean_orders, clean_products


def sample_tables():
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o2"],
            "customer_id": ["c1", "c2", "c2"],
            "order_status": [" Delivered", "canceled", "canceled"],
            "order_purchase_timestamp": ["2018-01-01 10:00:00", "2018-01-03 09:00:00", "2018-01-03 09:00:00"],
            "order_approved_at": ["2018-01-01 11:00:00", None, None],
            "order_delivered_carrier_date": [None, None, None],
            "order_delivered_customer_date": [None, None, None],
            "order_estimated_delivery_date": ["2018-01-10", "2018-01-12", "2018-01-12"],
        }
    )
    items = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "order_item_id": [1, 2, 1],
            "product_id": ["p1", "p2", "p1"],
            "seller_id": ["s1", "s1", "s2"],
            "shipping_limit_date": ["2018-01-02", "2018-01-02", "2018-01-04"],
            "price": [10.0, 5.5, 20.0],
            "freight_value": [2.0, 1.0, 3.0],
        }
    )
    customers = pd.DataFrame(
        {
            "customer_id": ["c1", "c2"],
            "customer_unique_id": ["u1", "u2"],
            "customer_zip_code_prefix": [1000, 2000],
            "customer_city": [" sao paulo", "rio de janeiro"],
            "customer_state": ["sp", "RJ"],
        }
    )
    products = pd.DataFrame(
        {
            "product_id": ["p1", "p2"],
            "product_category_name": ["beleza_saude", None],
            "product_weight_g": [100.0, 200.0],
            "product_photos_qty": [1.0, None],
        }
    )
    translation = pd.DataFrame(
        {"product_category_name": ["beleza_saude"], "product_category_name_english": ["health_beauty"]}
    )
    return {
        "orders": clean_orders(orders),
        "items": clean_items(items),
        "customers": clean_customers(customers, salt="test"),
        "products": clean_products(products, translation),
    }


def test_transform_cleans_and_pseudonymizes():
    t = sample_tables()
    assert len(t["orders"]) == 2
    assert t["orders"]["order_status"].tolist() == ["delivered", "canceled"]
    c = t["customers"]
    assert "customer_unique_id" not in c.columns
    assert c["customer_uid_hash"].str.len().eq(16).all()
    assert c["customer_city"].tolist() == ["Sao Paulo", "Rio De Janeiro"]
    assert t["products"]["category"].tolist() == ["health_beauty", "unknown"]


def test_star_schema_passes_quality(tmp_path):
    con = load(sample_tables(), db_path=":memory:")
    assert con.execute("SELECT count(*) FROM fact_sales").fetchone()[0] == 3
    assert run_checks(con, log=tmp_path / "log.csv") == []
    # pesanan canceled tidak dihitung di mart
    assert con.execute("SELECT sum(revenue) FROM mart_sales_monthly").fetchone()[0] == 15.5


def test_quality_catches_bad_price(tmp_path):
    t = sample_tables()
    t["items"].loc[0, "price"] = -1
    con = load(t, db_path=":memory:")
    assert run_checks(con, log=tmp_path / "log.csv") == ["fact_sales: price tidak boleh negatif atau nol"]
