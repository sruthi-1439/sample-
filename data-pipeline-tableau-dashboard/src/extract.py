"""
Multi-source extract: sales CSV-like, marketing API-like, support tickets.
"""
import numpy as np
import pandas as pd


def extract_sales(n=15000, seed=31):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "sale_id": np.arange(1, n + 1),
        "date": pd.to_datetime("2024-01-01") + pd.to_timedelta(
            rng.integers(0, 365, size=n), unit="D"),
        "region": rng.choice(["North", "South", "East", "West"], size=n),
        "rep_id": rng.integers(1, 101, size=n),
        "product": rng.choice(["Widget A", "Widget B", "Gadget X",
                               "Gadget Y"], size=n),
        "units": rng.integers(1, 20, size=n),
        "revenue": np.round(rng.uniform(50, 2000, size=n), 2),
    })
    df.loc[df.sample(100, random_state=8).index, "revenue"] = np.nan
    return df


def extract_marketing(n=365, seed=32):
    """Simulates a marketing-spend API: one row per day per channel."""
    rng = np.random.default_rng(seed)
    days = pd.date_range("2024-01-01", periods=n)
    rows = []
    for ch in ["paid_search", "social", "email", "display"]:
        spend = rng.uniform(200, 2000, size=n).round(2)
        rows.append(pd.DataFrame({
            "date": days, "channel": ch, "spend": spend,
            "impressions": rng.integers(5000, 200000, size=n)}))
    return pd.concat(rows, ignore_index=True)


def extract_support(n=3000, seed=33):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "ticket_id": np.arange(1, n + 1),
        "date": pd.to_datetime("2024-01-01") + pd.to_timedelta(
            rng.integers(0, 365, size=n), unit="D"),
        "region": rng.choice(["North", "South", "East", "West"], size=n),
        "csat": rng.integers(1, 6, size=n),  # 1-5 scale
        "resolution_hours": np.round(rng.exponential(20, size=n), 1),
    })
