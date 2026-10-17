# Healthcare Data Analytics & AI-Driven Reporting

End-to-end payer analytics pipeline on **synthetic** claims data (no real PHI):
SQL analysis, ML anomaly detection, cost prediction, patient segmentation,
and an automated validation workflow with before/after accuracy reporting.

## What it does

1. **Synthetic data** (`src/data_gen.py`) — 10,000 claims across 4,000 members
   with diagnosis-driven costs, age effects, and 60 injected fraud cases.
2. **SQL analysis** (`src/analysis.py`) — payer-style queries: spend by plan,
   top diagnoses by cost, high-cost members, monthly trends (via SQLite).
3. **Anomaly detection** — Isolation Forest flags suspicious claims for
   payment-integrity review; recall measured against injected fraud labels.
4. **Cost prediction** — Ridge regression on log-costs, trained on
   adjudicated (non-anomalous) claims only, as in production payer models.
5. **Patient segmentation** — K-Means on member aggregates identifies
   utilization segments (e.g. low-cost healthy vs. chronic high utilizers).
6. **Validation workflow** (`src/validation.py`) — logs every run's metrics to
   `output/validation_log.jsonl` and prints a before/after report vs.
   simulated legacy rule-based baselines.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Sample output

```
[anomaly] flagged 200 anomalous claims; recall on injected fraud: 50.0%
[regression] claim-cost model (n=9800 clean claims): MAE=$112, R²=0.484
[segments] patient utilization segments:
         members  avg_cost  avg_claims
segment
0           1231     753.4         1.9
...
[validation] BEFORE / AFTER accuracy report
  Fraud detection recall       before=0.45  after=0.50 (+11%)
  Claim-cost prediction R²     before=0.40  after=0.48 (+21%)
```

## Technologies

Python, pandas, NumPy, scikit-learn (Isolation Forest, Ridge, K-Means),
SQLite. Mirrors payer data-warehouse + AI reporting patterns.
