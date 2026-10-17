# Retail Banking Data Analytics & Reporting Automation

Chunked analytics pipeline over a **partitioned Parquet transaction lake** —
built to scale to 10M+ rows without ever holding the full dataset in memory.

## Architecture

```
synthetic generator ──▶ data/month=YYYY-MM/*.parquet ──▶ chunked readers ──▶ reports/
      (streaming          (columnar, monthly                 (pandas, bounded
       chunks)            partitions)                          memory)
```

## What it does

1. **Chunked generation** (`src/data_gen.py`) — streams synthetic card/online/
   branch/ATM transactions into monthly Parquet partitions. `TOTAL_ROWS`
   controls scale (default 1M demo; set `TOTAL_ROWS=10000000` for full scale).
2. **Query optimization showcase** (`src/optimize.py`) — timed comparison of
   three access patterns: naive full scan vs. partition pruning vs. pruned +
   sorted-key lookup. Demonstrates why warehouse partitioning and sort keys
   matter (pruning reads ~2/12 of the lake instead of all of it).
3. **EDA + customer behavior** (`src/analysis.py`) — chunked scans compute
   dataset profile, category/channel mix, and an RFM-style per-customer
   snapshot (transaction count, spend, top "whale" customers).
4. **Automated reporting** (`src/reporting.py`) — generates weekly and monthly
   markdown summary reports (volume, avg ticket, breakdowns by category and
   channel), replacing manual Excel reporting.

## How to run

```bash
pip install -r requirements.txt
python main.py                              # 1M-row demo (~30s)
TOTAL_ROWS=10000000 python main.py          # full 10M scale
```

## Sample output

```
[gen] 1,000,000 transactions -> data/ (monthly partitions)
[optimize] query patterns over partitioned Parquet lake:
  1. naive full scan      : 0.42s
  2. partition pruning    : 0.01s -> $19,902,361
[eda] rows: 1,000,000   total volume: $121,178,115   avg ticket: $121.18
[report] wrote reports/weekly_report.md
[report] wrote reports/monthly_report.md
```

## Technologies

Python, pandas, NumPy, PyArrow (Parquet). Patterns mirror Redshift/Snowflake
partition pruning, sort keys, and scheduled reporting jobs.
