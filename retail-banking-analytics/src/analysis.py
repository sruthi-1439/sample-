"""
EDA + customer behavior analysis over the partitioned lake.
Reads partitions in chunks to stay memory-light at 10M+ scale.
"""
import os
import pandas as pd


def iter_partitions(data_dir, columns=None, chunksize_months=3):
    months = sorted(d for d in os.listdir(data_dir)
                    if d.startswith("month="))
    for i in range(0, len(months), chunksize_months):
        frames = []
        for m in months[i:i + chunksize_months]:
            p = os.path.join(data_dir, m, "data.parquet")
            frames.append(pd.read_parquet(p, columns=columns))
        yield pd.concat(frames, ignore_index=True)


def eda_summary(data_dir):
    print("[eda] dataset profile (chunked scan):")
    total, amount_sum = 0, 0.0
    cat_totals, chan_counts = {}, {}
    for chunk in iter_partitions(data_dir,
                                 columns=["amount", "category", "channel"]):
        total += len(chunk)
        amount_sum += chunk["amount"].sum()
        for k, v in chunk["category"].value_counts().items():
            cat_totals[k] = cat_totals.get(k, 0) + int(v)
        for k, v in chunk["channel"].value_counts().items():
            chan_counts[k] = chan_counts.get(k, 0) + int(v)
    print(f"  rows: {total:,}   total volume: ${amount_sum:,.0f}   "
          f"avg ticket: ${amount_sum / total:,.2f}")
    top_cat = sorted(cat_totals.items(), key=lambda kv: -kv[1])[:3]
    print(f"  top categories: {', '.join(f'{k} ({v:,})' for k, v in top_cat)}")
    print(f"  channels: {', '.join(f'{k} ({v:,})' for k, v in chan_counts.items())}")
    return {"rows": total, "volume": amount_sum}


def customer_behavior(data_dir, top_n=5):
    print("[behavior] customer RFM-style snapshot (chunked):")
    agg = {}
    for chunk in iter_partitions(
            data_dir, columns=["customer_id", "amount", "txn_date"]):
        g = chunk.groupby("customer_id").agg(
            txns=("amount", "size"), spend=("amount", "sum"),
            last=("txn_date", "max"))
        for cid, row in g.iterrows():
            a = agg.setdefault(cid, [0, 0.0, row["last"]])
            a[0] += int(row["txns"])
            a[1] += float(row["spend"])
            if row["last"] > a[2]:
                a[2] = row["last"]
    cust = pd.DataFrame(
        [(cid, v[0], v[1]) for cid, v in agg.items()],
        columns=["customer_id", "txns", "spend"])
    print(f"  customers: {len(cust):,}   "
          f"avg txns/customer: {cust['txns'].mean():.1f}   "
          f"avg spend/customer: ${cust['spend'].mean():,.0f}")
    whales = cust.nlargest(top_n, "spend")
    print(f"  top {top_n} customers by spend:")
    print(whales.to_string(index=False))
    return cust
