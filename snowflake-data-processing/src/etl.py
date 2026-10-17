"""
ETL: extract -> clean -> transform -> validate.

Mirrors a Snowflake ELT flow: raw landing tables, dbt-style cleaning CTEs,
then validated marts. Data-quality checks gate every stage.
"""
import numpy as np
import pandas as pd

from .quality import run_quality_suite


def extract(n_orders=20000, seed=11):
    rng = np.random.default_rng(seed)
    orders = pd.DataFrame({
        "order_id": np.arange(1, n_orders + 1),
        "customer_id": rng.integers(1, 5001, size=n_orders),
        "product_id": rng.integers(1, 501, size=n_orders),
        "quantity": rng.integers(1, 10, size=n_orders),
        "unit_price": np.round(rng.uniform(5, 500, size=n_orders), 2),
        "order_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(
            rng.integers(0, 730, size=n_orders), unit="D"),
    })
    # dirty data for the quality suite to catch
    orders.loc[orders.sample(80, random_state=5).index, "quantity"] = -2
    orders.loc[orders.sample(40, random_state=6).index, "customer_id"] = np.nan
    orders = pd.concat([orders, orders.sample(25, random_state=7)],
                       ignore_index=True)
    products = pd.DataFrame({
        "product_id": np.arange(1, 501),
        "category": rng.choice(["A", "B", "C", "D"], size=500),
    })
    print(f"[extract] {len(orders)} raw orders, {len(products)} products")
    return orders, products


def clean(orders):
    """dbt-style cleaning: quarantine invalid rows, dedupe, type."""
    q = orders[(orders["quantity"] <= 0) | (orders["customer_id"].isna())]
    clean = orders[~orders.index.isin(q.index)].copy()
    clean = clean.drop_duplicates(subset=["order_id"], keep="first")
    clean["customer_id"] = clean["customer_id"].astype(int)
    clean["order_date"] = pd.to_datetime(clean["order_date"])
    clean["line_total"] = (clean["quantity"] * clean["unit_price"]).round(2)
    print(f"[clean] quarantined {len(q)} rows; {len(clean)} clean orders")
    return clean, q


def transform(clean, products):
    """Build marts: monthly customer revenue with lifetime + rolling stats."""
    clean["order_month"] = clean["order_date"].dt.to_period("M").astype(str)
    monthly = (clean.groupby(["customer_id", "order_month"])
               .agg(orders=("order_id", "count"),
                    revenue=("line_total", "sum")).reset_index()
               .sort_values(["customer_id", "order_month"]))
    monthly["lifetime_revenue"] = monthly.groupby("customer_id")[
        "revenue"].cumsum()
    monthly["rolling_3mo_avg"] = (monthly.groupby("customer_id")["revenue"]
                                  .transform(lambda s: s.rolling(3,
                                                                min_periods=1
                                                                ).mean())
                                  .round(2))
    monthly["revenue_rank_in_month"] = (monthly.groupby("order_month")
                                        ["revenue"].rank(ascending=False,
                                                         method="min")
                                        .astype(int))
    enriched = clean.merge(products, on="product_id", how="left")
    return monthly, enriched


def run_etl():
    raw_orders, products = extract()
    rep_raw = run_quality_suite(raw_orders, "raw_orders", strict=False)
    clean_orders, quarantine = clean(raw_orders)
    marts, enriched = transform(clean_orders, products)
    rep_clean = run_quality_suite(clean_orders, "clean_orders", strict=True)
    return {"marts": marts, "enriched": enriched,
            "quarantine": quarantine,
            "reports": [rep_raw, rep_clean]}
