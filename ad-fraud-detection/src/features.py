"""
Feature engineering for fraud signals.

Per-IP aggregates capture the classic fraud tells:
- click frequency (farms click far more than humans)
- IP entropy of app mix (farms hammer 1-2 apps; humans spread out)
- time regularity (bots click metronomically; humans are bursty)
- night share (farms often run 24/7)
"""
import numpy as np
import pandas as pd


def _entropy(probs):
    probs = np.array(probs)
    probs = probs[probs > 0]
    return float(-(probs * np.log2(probs)).sum())


def engineer(df):
    df = df.copy()
    df["hour"] = df["click_ts"].dt.hour
    feats = []
    for ip, g in df.groupby("ip"):
        g = g.sort_values("click_ts")
        n = len(g)
        gaps = g["click_ts"].diff().dt.total_seconds().dropna()
        app_mix = g["app_id"].value_counts(normalize=True)
        feats.append({
            "ip": ip,
            "clicks": n,
            "unique_apps": g["app_id"].nunique(),
            "app_entropy": _entropy(app_mix),
            "median_gap_s": float(gaps.median()) if len(gaps) else 3600.0,
            "gap_cv": float(gaps.std() / gaps.mean()) if len(gaps) > 1
                      and gaps.mean() > 0 else 1.0,
            "night_share": float(((g["hour"] < 6)).mean()),
            "fraud_rate": float(g["is_fraud"].mean()),
        })
    feat = pd.DataFrame(feats)
    print(f"[features] engineered {len(feat)} IP-level feature rows")
    return feat
