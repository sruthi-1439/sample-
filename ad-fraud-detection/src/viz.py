"""
Visualize fraud indicators + export BI-ready summary.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "output")


def visualize(feat):
    os.makedirs(OUT, exist_ok=True)
    feat = feat.copy()
    feat["label"] = (feat["fraud_rate"] > 0.5).map({True: "fraud",
                                                   False: "legit"})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    specs = [(axes[0, 0], "clicks", "Clicks per IP", False),
             (axes[0, 1], "app_entropy", "App-mix entropy per IP", False),
             (axes[1, 0], "median_gap_s",
              "Median inter-click gap (s, log scale)", True),
             (axes[1, 1], "night_share", "Night-time click share", False)]
    for ax, col, title, logx in specs:
        for lab in ["legit", "fraud"]:
            vals = feat.loc[feat["label"] == lab, col].clip(1)
            ax.hist(vals, bins=30, alpha=0.5, label=lab)
        if logx:
            ax.set_xscale("log")
        ax.set_title(title)
        ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fraud_indicators.png"), dpi=120)
    plt.close(fig)
    print(f"[viz] saved output/fraud_indicators.png")


def export_summary(feat):
    feat["label"] = (feat["fraud_rate"] > 0.5).map({True: "fraud",
                                                   False: "legit"})
    summary = feat.groupby("label").agg(
        ips=("ip", "count"),
        avg_clicks=("clicks", "mean"),
        avg_app_entropy=("app_entropy", "mean"),
        avg_night_share=("night_share", "mean"),
        flagged_iso=("iso_anomaly", "mean"),
        avg_rf_proba=("rf_fraud_proba", "mean")).round(3)
    path = os.path.join(OUT, "fraud_summary_bi.csv")
    summary.to_csv(path)
    print("[bi] Power BI / Tableau-ready summary:")
    print(summary.to_string())
    print(f"  saved {path}")
    return summary
