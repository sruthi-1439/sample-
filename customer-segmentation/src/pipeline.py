"""
Segmentation pipeline: clean -> EDA -> features -> elbow -> K-Means ->
profile -> visualize.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

OUT = os.path.join(os.path.dirname(__file__), "..", "output")


def clean(df):
    n0 = len(df)
    df = df.dropna(subset=["income_k"]).drop_duplicates(
        subset=["customer_id"])
    print(f"[clean] {n0} -> {len(df)} rows "
          f"({n0 - len(df)} dirty rows removed)")
    return df


def engineer_features(df):
    df = df.copy()
    df["spend_per_txn"] = (df["annual_spend"] / df["annual_txns"].clip(1)
                           ).round(2)
    df["txn_frequency"] = (df["annual_txns"] / 12).round(1)  # per month
    return df


def elbow_method(X_scaled, k_range=range(2, 9)):
    os.makedirs(OUT, exist_ok=True)
    inertias = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(list(k_range), inertias, "o-")
    ax.set_xlabel("k (clusters)")
    ax.set_ylabel("Inertia")
    ax.set_title("Elbow method for k selection")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "elbow.png"), dpi=120)
    plt.close(fig)
    # knee: largest relative drop reduction
    drops = np.diff(inertias)
    rel = drops[1:] / drops[:-1]
    k_star = list(k_range)[int(np.argmin(rel)) + 1]
    print(f"[elbow] inertias: {[round(i) for i in inertias]} -> "
          f"selected k={k_star} (see output/elbow.png)")
    return k_star


def cluster(df, feature_cols):
    Xs = StandardScaler().fit_transform(df[feature_cols])
    k = elbow_method(Xs)
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    df = df.copy()
    df["segment"] = km.fit_predict(Xs)
    return df, k


def profile(df):
    prof = df.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_age=("age", "mean"),
        avg_income_k=("income_k", "mean"),
        avg_tenure=("tenure_years", "mean"),
        avg_txns=("annual_txns", "mean"),
        avg_spend=("annual_spend", "mean")).round(1)
    print("[profile] segment characteristics:")
    print(prof.to_string())
    return prof


def visualize(df, profile):
    os.makedirs(OUT, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for seg, g in df.groupby("segment"):
        axes[0].scatter(g["annual_txns"], g["annual_spend"],
                        s=8, alpha=0.4, label=f"seg {seg}")
    axes[0].set_xlabel("Annual transactions")
    axes[0].set_ylabel("Annual spend ($)")
    axes[0].set_title("Segments: transactions vs spend")
    axes[0].legend()
    profile["avg_spend"].plot(kind="bar", ax=axes[1], color="steelblue")
    axes[1].set_xlabel("Segment")
    axes[1].set_ylabel("Avg annual spend ($)")
    axes[1].set_title("Avg spend per segment")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "segments.png"), dpi=120)
    plt.close(fig)
    print(f"[viz] saved output/segments.png, output/elbow.png")
