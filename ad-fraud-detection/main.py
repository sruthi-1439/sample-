"""
Mobile Ad Fraud Detection ("The Abser").

Synthetic click stream with injected fraud -> IP-level feature engineering
-> Isolation Forest + RandomForest -> fraud indicator charts + BI summary.

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.data_gen import generate_clicks
from src.features import engineer
from src.models import unsupervised, supervised
from src.viz import visualize, export_summary


def main():
    print("=" * 64)
    print("MOBILE AD FRAUD DETECTION — 'THE ABSER'")
    print("=" * 64)
    print("\n[1/5] generating synthetic click stream...")
    clicks = generate_clicks()

    print("\n[2/5] feature engineering (per-IP fraud signals)")
    feat = engineer(clicks)

    print("\n[3/5] unsupervised: Isolation Forest")
    feat = unsupervised(feat)
    print(f"  flagged {int(feat['iso_anomaly'].sum())} anomalous IPs")

    print("\n[4/5] supervised: RandomForest (vs injected labels)")
    feat, metrics = supervised(feat)

    print("\n[5/5] visualizations + BI export")
    visualize(feat)
    export_summary(feat)
    print("\nDone. See output/fraud_indicators.png + "
          "output/fraud_summary_bi.csv")


if __name__ == "__main__":
    main()
