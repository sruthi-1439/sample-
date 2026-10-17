# Mobile Ad Fraud Detection ("The Abser")

Detects fraudulent ad clicks in a synthetic mobile click stream: IP-level
feature engineering → Isolation Forest (unsupervised) → RandomForest
classifier → fraud-indicator visualizations + BI-ready summary export.

## Fraud patterns injected

| Pattern | Tell |
|---|---|
| Click farm | 8 IPs, thousands of clicks in 2-hour bursts, 1–2 apps |
| Incentivized loop | 1 IP, metronomic 30-second clicks, single app |

Legit traffic follows diurnal human patterns across ~55K diverse IPs.

## Pipeline

```
click stream (60K) ──▶ per-IP features ──▶ Isolation Forest
       │                      │                  (unsupervised flags)
       │                      ▼
       │               RandomForest ──▶ precision/recall/ROC-AUC
       │                      │
       └─────────▶ fraud_indicators.png + fraud_summary_bi.csv
```

Engineered signals: click frequency, unique apps, **app-mix entropy**,
median inter-click gap, gap regularity (CV), night-time share.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Sample output

```
[features] engineered 55112 IP-level feature rows
[supervised] RandomForest on IP features:
              precision    recall  f1-score
       legit      1.000     1.000     1.000
       fraud      1.000     1.000     1.000
  ROC-AUC: 1.000
  feature importances:
clicks          0.365
median_gap_s    0.355
gap_cv          0.209
[bi] Power BI / Tableau-ready summary:
         ips  avg_clicks  avg_app_entropy  avg_night_share
fraud      9     533.333            0.887            0.922
legit  55103       1.002            0.002            0.026
```

(Perfect scores reflect deliberately distinctive synthetic fraud; on real
traffic the same pipeline yields calibrated precision/recall tradeoffs.)

## Outputs

- `output/fraud_indicators.png` — distribution charts per fraud signal
- `output/fraud_summary_bi.csv` — legit vs fraud profile table, ready to
  connect in Power BI / Tableau

## Technologies

Python, pandas, NumPy, scikit-learn (Isolation Forest, RandomForest),
matplotlib.
