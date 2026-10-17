"""
Synthetic mobile ad-click stream with injected fraud patterns.

Legit traffic: diurnal human patterns, diverse IPs/devices.
Fraud: click farms (bursty high-frequency clicks from few IPs),
       incentivized loops (regular-interval clicks), device spoofing.
"""
import numpy as np
import pandas as pd


def generate_clicks(n=60000, seed=55, fraud_ratio=0.08):
    rng = np.random.default_rng(seed)
    n_fraud = int(n * fraud_ratio)
    n_legit = n - n_fraud

    def diurnal_times(k):
        # humans click more 8am-11pm
        p = np.array(
            [0.01, 0.005, 0.003, 0.002, 0.002, 0.004, 0.01, 0.03, 0.05,
             0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.07, 0.08,
             0.08, 0.07, 0.05, 0.03, 0.015])
        p = p / p.sum()
        hours = rng.choice(24, size=k, p=p)
        base = pd.to_datetime("2024-06-01")
        return base + pd.to_timedelta(hours, unit="h") + pd.to_timedelta(
            rng.integers(0, 3600, size=k), unit="s")

    legit = pd.DataFrame({
        "click_id": np.arange(1, n_legit + 1),
        "ip": [f"10.{rng.integers(0,255)}.{rng.integers(0,255)}."
               f"{rng.integers(1,254)}" for _ in range(n_legit)],
        "device": rng.choice(["android", "ios"], size=n_legit, p=[0.7, 0.3]),
        "app_id": rng.choice([f"app_{i}" for i in range(1, 51)],
                             size=n_legit),
        "click_ts": diurnal_times(n_legit),
        "is_fraud": 0,
    })

    # Fraud pattern A: click farm — many clicks, few IPs, tight bursts
    farm_ips = [f"192.168.{i}.10" for i in range(8)]
    fa = pd.DataFrame({
        "click_id": np.arange(n_legit + 1, n_legit + n_fraud // 2 + 1),
        "ip": rng.choice(farm_ips, size=n_fraud // 2),
        "device": "android",
        "app_id": rng.choice(["app_7", "app_13"], size=n_fraud // 2),
        "click_ts": (pd.to_datetime("2024-06-10")
                     + pd.to_timedelta(rng.integers(0, 7200,
                                                   size=n_fraud // 2),
                                       unit="s")),
        "is_fraud": 1,
    })
    # Fraud pattern B: incentivized loop — metronomic clicks, one IP/device
    base = pd.to_datetime("2024-06-15")
    fb = pd.DataFrame({
        "click_id": np.arange(n_legit + n_fraud // 2 + 1, n + 1),
        "ip": "172.16.0.99",
        "device": "android",
        "app_id": "app_42",
        "click_ts": [base + pd.Timedelta(seconds=30 * i)
                     for i in range(n - n_legit - n_fraud // 2)],
        "is_fraud": 1,
    })
    df = pd.concat([legit, fa, fb], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df["click_id"] = np.arange(1, len(df) + 1)
    print(f"[gen] {len(df):,} clicks ({df['is_fraud'].mean():.1%} injected "
          f"fraud)")
    return df
