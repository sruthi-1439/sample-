# Cloud Data Analytics & Snowflake Data Processing

Pandas/NumPy ETL with quality gates plus **Snowflake-dialect SQL analytics**
(joins, CTEs, window functions) — the `.sql` files are production-ready for
Snowflake, and a Python runner executes the equivalent logic locally for
verification.

## What it does

1. **ETL** (`src/etl.py`)
   - *Extract*: 20K synthetic orders + 500 products (with injected dirty rows).
   - *Clean*: dbt-style quarantine of negative quantities, null keys, and
     duplicates.
   - *Transform*: monthly customer-revenue marts with lifetime revenue,
     rolling 3-month averages, and in-month revenue ranks.
   - *Validate*: quality suite gates raw (lenient) and clean (strict) stages.
2. **SQL analytics** (`sql/*.sql`, Snowflake dialect)
   - `customer_lifetime_value.sql` — CTEs + window functions (`SUM OVER`,
     `RANK OVER`, rolling `AVG OVER`) for CLV marts.
   - `quality_anomaly_scan.sql` — join + CTE + z-score scan flagging orders
     far from their product norm.
3. **Runner** (`src/runner.py`) — ports both queries to SQLite (translating
   `DATE_TRUNC`, `STDDEV`, `TRY_CAST`) so results are verifiable without a
   warehouse.

## Data quality checks

Nulls in keys, duplicate order IDs, non-positive quantities/prices. Raw data
is expected to fail; the strict gate on clean data raises on any failure.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Sample output

```
[quality:raw_orders] 1/4 checks passed  <-- issues found
[clean] quarantined 145 rows; 19900 clean orders
[quality:clean_orders] 4/4 checks passed
[sql] customer lifetime value (window functions) — head:
 customer_id order_month  orders  revenue  lifetime_revenue ...
           1 2023-07          1  3276.77           3276.77 ...
```

## Technologies

Python, pandas, NumPy, SQLite — SQL written for Snowflake (CTEs, window
functions, `DATE_TRUNC`, `TRY_CAST`).
