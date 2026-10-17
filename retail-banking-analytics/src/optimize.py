"""
Query-optimization showcase: why partitioning + columnar storage matters.

Compares three access patterns over the transaction lake and prints timings:
  1. naive  — read every monthly partition, filter in pandas
  2. pruned — read only the partitions for the requested months
  3. indexed — pruned + pre-sorted customer_id (simulates a warehouse index)
"""
import os
import time
import pandas as pd


def _partitions_for(data_dir, months):
    paths = []
    for m in months:
        p = os.path.join(data_dir, f"month={m}", "data.parquet")
        if os.path.exists(p):
            paths.append(p)
    return paths


def naive_monthly_total(data_dir, months):
    t0 = time.perf_counter()
    frames = []
    for entry in sorted(os.listdir(data_dir)):
        p = os.path.join(data_dir, entry, "data.parquet")
        if os.path.isfile(p):
            frames.append(pd.read_parquet(p, columns=["txn_date", "amount"]))
    all_data = pd.concat(frames, ignore_index=True)
    all_data["month"] = all_data["txn_date"].dt.strftime("%Y-%m")
    out = all_data[all_data["month"].isin(months)].groupby("month")[
        "amount"].sum()
    return out, time.perf_counter() - t0


def pruned_monthly_total(data_dir, months):
    t0 = time.perf_counter()
    frames = [pd.read_parquet(p, columns=["amount"])
              for p in _partitions_for(data_dir, months)]
    total = (pd.concat(frames, ignore_index=True)["amount"].sum()
             if frames else 0.0)
    return total, time.perf_counter() - t0


def indexed_customer_lookup(data_dir, months, customer_id, n=5):
    """Simulates an indexed point lookup: partition prune + sorted scan."""
    t0 = time.perf_counter()
    hits = []
    for p in _partitions_for(data_dir, months):
        df = pd.read_parquet(p, columns=["customer_id", "amount",
                                         "category"]).sort_values(
                                             "customer_id")
        # binary-search style slice on the sorted key
        lo = df["customer_id"].searchsorted(customer_id, side="left")
        hi = df["customer_id"].searchsorted(customer_id, side="right")
        if hi > lo:
            hits.append(df.iloc[lo:hi])
    out = (pd.concat(hits, ignore_index=True).head(n)
           if hits else pd.DataFrame())
    return out, time.perf_counter() - t0


def demo(data_dir, months=("2024-01", "2024-02")):
    print("[optimize] query patterns over partitioned Parquet lake:")
    res, t = naive_monthly_total(data_dir, months)
    print(f"  1. naive full scan      : {t:.2f}s ->\n{res.to_string()}")
    total, t = pruned_monthly_total(data_dir, months)
    print(f"  2. partition pruning    : {t:.2f}s -> ${total:,.0f}")
    hits, t = indexed_customer_lookup(data_dir, months, customer_id=42)
    print(f"  3. pruned + sorted key  : {t:.2f}s -> "
          f"{len(hits)} txns for customer 42")
    print("  takeaway: partition pruning avoids reading 10/12 of the lake; "
          "sorted keys turn lookups into binary searches.")
