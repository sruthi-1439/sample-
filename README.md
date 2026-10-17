# Data Analytics Portfolio

Nine end-to-end data analytics projects — every one runs locally with
**synthetic data** (no real company data, no credentials needed).
Each project has its own `README.md`, `requirements.txt`, and a
`python main.py` entry point.

## Projects

| # | Project | What it demonstrates |
|---|---|---|
| 1 | [aws-data-warehouse-etl](aws-data-warehouse-etl/) | AWS-style ETL: S3 → Glue → Redshift (simulated), validation gates, quarantine, star schema |
| 2 | [healthcare-data-analytics-ai](healthcare-data-analytics-ai/) | Payer claims analytics: SQL, Isolation Forest fraud detection, cost regression, K-Means segments |
| 3 | [retail-banking-analytics](retail-banking-analytics/) | 10M+ row chunked pipeline, Parquet partitioning, query optimization, automated reporting |
| 4 | [snowflake-data-processing](snowflake-data-processing/) | Snowflake-dialect SQL (CTEs, window functions), ETL with quality gates |
| 5 | [cloud-data-lake](cloud-data-lake/) | Bronze/silver/gold lake, Lambda-like triggers, DuckDB "Athena" queries, HTML KPI dashboard |
| 6 | [customer-segmentation](customer-segmentation/) | K-Means with elbow method, segment profiling, business insights, matplotlib charts |
| 7 | [data-pipeline-tableau-dashboard](data-pipeline-tableau-dashboard/) | Multi-source ETL → Tableau-ready extracts → KPI dashboard, validation report |
| 8 | [sales-forecasting](sales-forecasting/) | Seasonal-naive vs ARIMA, holdout evaluation, Tableau-ready forecast export |
| 9 | [ad-fraud-detection](ad-fraud-detection/) | Click-fraud detection: feature engineering, Isolation Forest + RandomForest, BI summary |

## Quick start

```bash
# install shared dependencies
pip install -r requirements.txt

# run any project
cd aws-data-warehouse-etl && python main.py
cd ../healthcare-data-analytics-ai && python main.py
# ... etc.
```

Each project directory also has its own `requirements.txt` if you prefer
per-project installs.

## Tech stack

Python · pandas · NumPy · scikit-learn · statsmodels · matplotlib ·
PyArrow (Parquet) · DuckDB · SQLite
