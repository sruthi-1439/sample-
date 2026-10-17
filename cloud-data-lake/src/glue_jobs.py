"""
Glue-like ETL jobs: bronze -> silver -> gold.

In AWS these are Glue PySpark jobs triggered by crawlers/schedules.
Here they are pandas jobs with the same zone-promotion semantics.
"""
import numpy as np
import pandas as pd
from .lake import write_zone, read_zone


def bronze_ingest(root, n=30000, seed=21):
    """Simulate raw event ingestion into the bronze zone."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "event_id": np.arange(1, n + 1),
        "user_id": rng.integers(1, 8001, size=n),
        "event_type": rng.choice(["view", "click", "purchase", "signup"],
                                 size=n, p=[0.55, 0.25, 0.12, 0.08]),
        "amount": np.round(rng.exponential(45, size=n), 2),
        "event_ts": pd.to_datetime("2024-01-01") + pd.to_timedelta(
            rng.integers(0, 180, size=n), unit="D"),
        "country": rng.choice(["US", "UK", "CA", "DE", "AU"], size=n,
                              p=[0.5, 0.2, 0.1, 0.1, 0.1]),
    })
    df.loc[df.sample(200, random_state=9).index, "user_id"] = np.nan
    write_zone(root, "bronze", "events", df)
    return df


def silver_clean(root):
    """Glue job 1: deduplicate, drop bad keys, standardize types."""
    df = read_zone(root, "bronze", "events")
    clean = df.dropna(subset=["user_id", "event_ts"]).copy()
    clean = clean.drop_duplicates(subset=["event_id"])
    clean["user_id"] = clean["user_id"].astype(int)
    clean["event_ts"] = pd.to_datetime(clean["event_ts"])
    clean["event_date"] = clean["event_ts"].dt.date.astype(str)
    write_zone(root, "silver", "events_clean", clean)
    return clean


def gold_aggregate(root):
    """Glue job 2: daily KPI aggregates -> gold zone."""
    df = read_zone(root, "silver", "events_clean")
    daily = (df.groupby(["event_date", "event_type", "country"])
             .agg(events=("event_id", "count"),
                  users=("user_id", "nunique"),
                  revenue=("amount", "sum")).reset_index())
    daily["revenue"] = daily["revenue"].round(2)
    write_zone(root, "gold", "daily_kpis", daily)
    return daily
