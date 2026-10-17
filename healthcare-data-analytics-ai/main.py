"""
Healthcare Data Analytics & AI-Driven Reporting.

End-to-end: synthetic payer claims -> SQL analysis -> anomaly detection ->
cost prediction -> patient segmentation -> validation report.

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.data_gen import generate_claims
from src.analysis import run_sql_analysis
from src.models import detect_anomalies, predict_costs, segment_patients
from src.validation import log_metrics, before_after_report


def main():
    print("=" * 64)
    print("HEALTHCARE DATA ANALYTICS & AI-DRIVEN REPORTING")
    print("=" * 64)

    print("\n[1/5] generating synthetic payer claims data...")
    claims = generate_claims(n=10000)
    print(f"  {len(claims)} claims, {claims['member_id'].nunique()} members")

    print("\n[2/5] SQL claims analysis")
    run_sql_analysis(claims)

    print("\n[3/5] anomaly detection (payment integrity)")
    claims, anomaly_metrics = detect_anomalies(claims)
    log_metrics("anomaly_detection", anomaly_metrics)

    print("\n[4/5] claim-cost regression")
    _, reg_metrics = predict_costs(claims)
    log_metrics("cost_regression", reg_metrics)

    print("\n[5/5] patient segmentation")
    _, profile = segment_patients(claims)
    log_metrics("segmentation",
                {"n_segments": 4,
                 "profile": profile.to_dict()})

    measured = {"fraud_recall": anomaly_metrics["fraud_recall"],
                "r2": reg_metrics["r2"]}
    before_after_report(measured)
    print("\nDone. Validation log: output/validation_log.jsonl")


if __name__ == "__main__":
    main()
