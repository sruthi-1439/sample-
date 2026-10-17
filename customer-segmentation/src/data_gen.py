"""
Synthetic customer generator: demographics + behavioral features.
"""
import numpy as np
import pandas as pd


def generate_customers(n=5000, seed=42):
    rng = np.random.default_rng(seed)
    # Latent segments drive realistic feature correlations
    latent = rng.choice([0, 1, 2, 3], size=n, p=[0.35, 0.3, 0.2, 0.15])
    age = np.where(latent == 0, rng.normal(28, 6, n),
          np.where(latent == 1, rng.normal(45, 8, n),
          np.where(latent == 2, rng.normal(38, 7, n),
                   rng.normal(60, 8, n)))).clip(18, 85).astype(int)
    income = np.where(latent == 0, rng.normal(45, 12, n),
             np.where(latent == 1, rng.normal(95, 20, n),
             np.where(latent == 2, rng.normal(70, 15, n),
                      rng.normal(55, 14, n)))).clip(20, 200)
    tenure = np.array([rng.exponential([1.2, 5.5, 3.0, 8.0][l])
                       for l in latent]).clip(0.1, 15).round(1)
    txns = np.array([rng.poisson([25, 8, 40, 5][l]) for l in latent])
    spend = (txns * np.where(latent == 0, rng.normal(35, 10, n),
                np.where(latent == 1, rng.normal(120, 30, n),
                np.where(latent == 2, rng.normal(60, 15, n),
                         rng.normal(200, 50, n))))).clip(50).round(2)
    df = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "age": age,
        "income_k": np.round(income, 1),
        "tenure_years": tenure,
        "annual_txns": txns,
        "annual_spend": spend,
        "region": rng.choice(["North", "South", "East", "West"], size=n),
        "channel_pref": rng.choice(["online", "in-store", "both"], size=n,
                                   p=[0.45, 0.25, 0.3]),
    })
    # dirty rows for the cleaning step
    df.loc[df.sample(60, random_state=3).index, "income_k"] = np.nan
    df = pd.concat([df, df.sample(30, random_state=4)], ignore_index=True)
    return df
