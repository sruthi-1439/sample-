# AWS Cloud Data Warehouse & ETL Automation

Simulates a production AWS analytics pipeline — **S3 → Glue → Redshift** — using
local equivalents so the whole thing runs on any machine with Python.

## Architecture

```
 ┌────────────┐    ┌──────────────┐    ┌────────────────┐    ┌───────────┐
 │  Sources   │───▶│  S3 (raw)    │───▶│  AWS Glue jobs │───▶│ Redshift  │
 │ CSV / API  │    │ data_lake/   │    │  transform +   │    │ warehouse │
 │            │    │   /raw       │    │  QC gates      │    │analytics.db│
 └────────────┘    └──────────────┘    └────────────────┘    └───────────┘
                          │                    │  bad rows
                          │                    ▼  ─────────▶ quarantine/
                          │              ┌─────────────┐
                          └─────────────▶│ S3 (curated)│
                                         │  /curated   │
                                         └─────────────┘
```

| AWS component | Local simulation |
|---|---|
| S3 raw / curated zones | `data_lake/raw/`, `data_lake/curated/` (CSV → Parquet) |
| AWS Glue PySpark jobs | `src/transform.py` pandas jobs |
| Glue Data Quality | `src/validation.py` check framework |
| Redshift warehouse | SQLite `warehouse/analytics.db` (star schema) |
| S3 quarantine prefix | `data_lake/quarantine/` |

## Pipeline stages

1. **Extract** (`src/extract.py`) — generates three source datasets (customers,
   products, orders) with deliberately injected dirty rows (nulls, duplicates,
   negative prices) and lands them as CSV in the raw zone.
2. **Transform** (`src/transform.py`) — three Glue-like jobs clean the data,
   enforce foreign keys, derive `line_total`, and quarantine bad rows. Every
   job runs validation gates before and after.
3. **Load** (`src/load.py`) — loads curated Parquet into a SQLite star schema
   (`dim_customers`, `dim_products`, `fact_orders`) and runs a sample revenue-
   by-region mart query.

## Data validation framework

`src/validation.py` provides reusable checks: null detection, duplicate
detection, positivity, referential integrity, and row-count bounds. The demo
proves the framework works — raw-zone checks **fail** on the injected dirty
data while curated-zone checks **pass 8/8** after quarantining.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Sample output

```
[extract] landed 5000 customers, 500 products, 20020 orders
[transform] validation results:
  [fact_orders_curated] 8/8 checks passed
[load] warehouse ready: {'dim_customers': 5000, 'dim_products': 497, 'fact_orders': 19840}
[load] sample mart query — revenue by region (completed orders):
region  orders    revenue
 North    5568 6884575.34
 ...
```

## Technologies

Python, pandas, NumPy, PyArrow (Parquet), SQLite — mirroring AWS S3, Glue,
and Redshift patterns.
