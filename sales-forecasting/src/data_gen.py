"""
Synthetic daily sales with trend + weekly/yearly seasonality + noise,
plus realistic promo spikes.
"""
import numpy as np
import pandas as pd


def generate_sales(days=730, seed=77):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=days, freq="D")
    t = np.arange(days)
    trend = 500 + 0.35 * t
    weekly = 80 * np.sin(2 * np.pi * t / 7)
    yearly = 150 * np.sin(2 * np.pi * t / 365.25)
    noise = rng.normal(0, 40, size=days)
    promo = np.zeros(days)
    for start in rng.choice(days - 14, size=12, replace=False):
        promo[start:start + 7] += rng.uniform(150, 300)
    sales = np.maximum(50, trend + weekly + yearly + noise + promo)
    return pd.DataFrame({"date": dates,
                         "sales": np.round(sales, 2)}).set_index("date")
