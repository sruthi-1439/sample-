# Data Pipeline Automation & Analytics Dashboard

Multi-source ETL pipeline producing **Tableau-ready extracts** plus a
Python-generated **HTML KPI dashboard** that mirrors the Tableau view.

## Pipeline

```
sales (15K) ──┐
marketing ────┼──▶ clean/validate ──▶ marts ──▶ extracts/*.csv ──▶ dashboard.html
support ──────┘         │                    (Tableau connects
                   quarantine/          natively + data dictionary)
```

## What it does

1. **Extract** (`src/extract.py`) — three sources: sales transactions,
   marketing spend/impressions (API-like), support tickets with CSAT.
2. **Transform** (`src/pipeline.py`) — cleans nulls, builds four marts:
   `sales_mart` (month × region × product), `spend_mart` (month × channel),
   `roas` (revenue/spend efficiency), `csat_mart` (support quality).
3. **Validate** — quality report gates the extracts (nulls, dupes,
   non-negative revenue); bad rows quarantined.
4. **Tableau extracts** (`extracts/`) — optimized CSVs at dashboard grain
   plus `_data_dictionary.csv` for field mapping. (Hyper extracts would use
   the Tableau Hyper API; CSV keeps this dependency-light while Tableau
   connects natively.)
5. **Dashboard** (`src/dashboard.py`) — KPI cards (revenue, ROAS, CSAT) and
   bar views for monthly trend, regional mix, ROAS, and CSAT.

## How to run

```bash
pip install -r requirements.txt
python main.py
# open output/dashboard.html; connect Tableau to extracts/*.csv
```

## Sample output

```
[validation] Tableau extract quality report:
  PASS: sales.revenue no nulls — 0 nulls
  PASS: sales.sale_id unique — 0 dupes
[extracts] 4 Tableau-ready CSVs -> extracts/
[dashboard] -> output/dashboard.html
```

## Technologies

Python, pandas, NumPy — ETL + validation patterns feeding Tableau.
