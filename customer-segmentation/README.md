# Customer Segmentation Analysis

Full clustering pipeline on synthetic customer data: cleaning → EDA →
feature engineering → **K-Means with elbow-method k selection** → segment
profiling → matplotlib visualizations.

## Pipeline

```
synthetic customers ──▶ clean (nulls, dupes) ──▶ feature engineering
        ──▶ standardize ──▶ elbow method ──▶ K-Means ──▶ profile + charts
```

Engineered features: `spend_per_txn`, `txn_frequency` (per month), plus raw
demographics and behavioral metrics.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Sample output

```
[clean] 5030 -> 4940 rows (90 dirty rows removed)
[elbow] inertias: [18820, 13421, 10644, 9048, 8365, ...] -> selected k=5
[profile] segment characteristics:
         customers  avg_age  avg_income_k  avg_txns  avg_spend
segment
0             1109     44.2          96.7       7.9      939.8
1              911     38.0          69.8      40.4     2457.9
2             1831     27.7          45.6      25.0      868.5
...
[viz] saved output/segments.png, output/elbow.png
```

## Business insights per segment (example run)

| Segment | Profile | Business takeaway |
|---|---|---|
| Young frequent shoppers | Age ~28, 25 txns/yr, modest spend | High engagement, low basket — target with bundle/upsell offers |
| Power users | 40 txns/yr, ~$2.5K spend | Top value cohort — VIP retention, early access programs |
| Affluent low-frequency | High income, ~8 txns/yr | Large basket potential — personalized high-ticket campaigns |
| Loyal long-tenure | ~13 yrs tenure, steady spend | Brand advocates — referral incentives, loyalty rewards |
| Older traditionalists | Age ~60, few txns | In-store/service focus — simplify digital journeys |

(Segment labels shift slightly per run; the profiling table is the source of truth.)

## Technologies

Python, pandas, NumPy, scikit-learn (StandardScaler, K-Means),
matplotlib (Agg backend — PNGs saved to `output/`).
