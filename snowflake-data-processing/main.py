"""
Cloud Data Analytics & Snowflake Data Processing.

ETL (extract/clean/transform/validate) + Snowflake-dialect SQL analytics
(joins, CTEs, window functions) executed locally for verification.

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.etl import run_etl
from src.runner import run_sql_suite


def main():
    print("=" * 64)
    print("SNOWFLAKE DATA PROCESSING — ETL + SQL ANALYTICS")
    print("=" * 64)
    print("\n[1/2] ETL with quality gates")
    out = run_etl()
    print(f"  marts: {len(out['marts']):,} customer-month rows; "
          f"quarantined: {len(out['quarantine'])} rows")
    print("\n[2/2] Snowflake-dialect SQL (verified on SQLite)")
    run_sql_suite(out["enriched"])
    print("\nDone. Production SQL lives in sql/*.sql (Snowflake dialect).")


if __name__ == "__main__":
    main()
