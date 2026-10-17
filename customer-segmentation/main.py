"""
Customer Segmentation Analysis.

Synthetic customers -> cleaning -> EDA -> feature engineering ->
K-Means (elbow-selected k) -> segment profiling -> visualizations.

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.data_gen import generate_customers
from src.pipeline import (clean, engineer_features, cluster, profile,
                          visualize)

FEATURES = ["age", "income_k", "tenure_years", "annual_txns",
            "annual_spend", "spend_per_txn", "txn_frequency"]


def main():
    print("=" * 64)
    print("CUSTOMER SEGMENTATION ANALYSIS")
    print("=" * 64)
    print("\n[1/5] generating synthetic customers...")
    df = generate_customers()
    print(f"  {len(df)} rows (incl. dirty rows for cleaning demo)")

    print("\n[2/5] cleaning + feature engineering")
    df = engineer_features(clean(df))

    print("\n[3/5] K-Means clustering (elbow method selects k)")
    df, k = cluster(df, FEATURES)

    print("\n[4/5] segment profiling")
    prof = profile(df)

    print("\n[5/5] visualizations")
    visualize(df, prof)
    print("\nDone. Charts: output/elbow.png, output/segments.png")


if __name__ == "__main__":
    main()
