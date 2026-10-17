"""
Chunked synthetic transaction generator.

Generates data in chunks so the pipeline scales to 10M+ rows without
holding everything in memory. Demo default is 1M rows; override with
TOTAL_ROWS for the full-scale run.
"""
import os
import numpy as np
import pandas as pd

MERCHANTS = [f"MCH{i:04d}" for i in range(1, 201)]
CATEGORIES = ["Groceries", "Dining", "Travel", "Utilities", "Shopping",
              "Healthcare", "Entertainment", "Transport"]


def _chunk(rng, start_id, n, n_customers):
    cat = rng.choice(CATEGORIES, size=n,
                     p=[0.25, 0.18, 0.08, 0.1, 0.15, 0.07, 0.07, 0.1])
    base = {"Groceries": 60, "Dining": 35, "Travel": 400, "Utilities": 120,
            "Shopping": 90, "Healthcare": 150, "Entertainment": 45,
            "Transport": 25}
    amounts = np.array([base[c] for c in cat]) * rng.lognormal(0, 0.7, size=n)
    return pd.DataFrame({
        "txn_id": np.arange(start_id, start_id + n),
        "customer_id": rng.integers(1, n_customers + 1, size=n),
        "merchant_id": rng.choice(MERCHANTS, size=n),
        "category": cat,
        "amount": np.round(amounts, 2),
        "txn_date": pd.to_datetime("2024-01-01") + pd.to_timedelta(
            rng.integers(0, 365, size=n), unit="D"),
        "channel": rng.choice(["card", "online", "branch", "atm"], size=n,
                              p=[0.55, 0.3, 0.1, 0.05]),
    })


def generate_transactions(total_rows=1_000_000, n_customers=200_000,
                         chunk_size=200_000, out_dir="data",
                         seed=42, partition_by_month=True):
    """Write transactions as monthly Parquet partitions (chunked)."""
    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    written = 0
    start_id = 1
    buffers = {}
    while written < total_rows:
        n = min(chunk_size, total_rows - written)
        df = _chunk(rng, start_id, n, n_customers)
        df["month"] = df["txn_date"].dt.strftime("%Y-%m")
        for month, g in df.groupby("month"):
            part_dir = os.path.join(out_dir, f"month={month}")
            os.makedirs(part_dir, exist_ok=True)
            path = os.path.join(part_dir, "data.parquet")
            chunk = g.drop(columns=["month"])
            if os.path.exists(path):
                # append: read-merge-write (keeps dependencies light)
                prev = pd.read_parquet(path)
                chunk = pd.concat([prev, chunk], ignore_index=True)
            chunk.to_parquet(path, index=False)
        written += n
        start_id += n
        print(f"  ... {written:,}/{total_rows:,} rows written", end="\r")
    print(f"\n[gen] {written:,} transactions -> {out_dir}/ (monthly partitions)")
    return out_dir
