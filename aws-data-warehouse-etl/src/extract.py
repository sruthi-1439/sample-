"""
Extract stage — simulates pulling data from multiple source systems
into an S3-like raw landing zone (local folders stand in for S3 buckets).

In AWS this would be: on-prem DBs / SaaS APIs -> S3 (raw zone).
Locally: synthetic generators -> data_lake/raw/
"""
import os
import numpy as np
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data_lake", "raw")


def generate_customers(n=5000, seed=42):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "customer_name": [f"Customer_{i:05d}" for i in range(1, n + 1)],
        "email": [f"customer{i:05d}@example.com" for i in range(1, n + 1)],
        "region": rng.choice(["North", "South", "East", "West"], size=n,
                             p=[0.3, 0.25, 0.25, 0.2]),
        "signup_date": pd.to_datetime("2020-01-01") + pd.to_timedelta(
            rng.integers(0, 1500, size=n), unit="D"),
        "is_active": rng.choice([True, False], size=n, p=[0.85, 0.15]),
    })


def generate_products(n=500, seed=7):
    rng = np.random.default_rng(seed)
    categories = ["Electronics", "Apparel", "Home", "Sports", "Grocery"]
    df = pd.DataFrame({
        "product_id": np.arange(1, n + 1),
        "product_name": [f"Product_{i:04d}" for i in range(1, n + 1)],
        "category": rng.choice(categories, size=n),
        "unit_price": np.round(rng.uniform(5, 500, size=n), 2),
    })
    # Inject a few dirty rows to exercise the validation framework
    df.loc[df.sample(3, random_state=1).index, "unit_price"] = -10.0
    return df


def generate_orders(n=20000, n_customers=5000, n_products=500, seed=99):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "order_id": np.arange(1, n + 1),
        "customer_id": rng.integers(1, n_customers + 1, size=n),
        "product_id": rng.integers(1, n_products + 1, size=n),
        "quantity": rng.integers(1, 10, size=n),
        "order_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(
            rng.integers(0, 730, size=n), unit="D"),
        "status": rng.choice(["completed", "completed", "completed",
                              "cancelled", "returned"],
                             size=n, p=[0.8, 0.05, 0.05, 0.05, 0.05]),
    })
    # Inject dirty rows: nulls + duplicates, caught downstream
    df.loc[df.sample(50, random_state=2).index, "customer_id"] = np.nan
    df = pd.concat([df, df.sample(20, random_state=3)], ignore_index=True)
    return df


def extract_all(base_dir=RAW_DIR):
    """Simulate the extract: land three source datasets as CSV in raw zone."""
    os.makedirs(base_dir, exist_ok=True)
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders()
    customers.to_csv(os.path.join(base_dir, "customers.csv"), index=False)
    products.to_csv(os.path.join(base_dir, "products.csv"), index=False)
    orders.to_csv(os.path.join(base_dir, "orders.csv"), index=False)
    print(f"[extract] landed {len(customers)} customers, {len(products)} "
          f"products, {len(orders)} orders -> {base_dir}")
    return {"customers": customers, "products": products, "orders": orders}
