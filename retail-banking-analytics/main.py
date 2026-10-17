"""
Retail Banking Data Analytics & Reporting Automation.

Chunked pipeline over a partitioned Parquet transaction lake:
  generate -> optimize demo -> EDA -> behavior -> automated reports.

Run:  python main.py            (1M-row demo, fast)
        TOTAL_ROWS=10000000 python main.py   (full 10M scale)

The generator streams in chunks, so 10M+ rows never sit in memory at once.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.data_gen import generate_transactions
from src.optimize import demo as optimize_demo
from src.analysis import eda_summary, customer_behavior
from src.reporting import generate_reports


def main():
    total = int(os.environ.get("TOTAL_ROWS", "1000000"))
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    print("=" * 64)
    print("RETAIL BANKING DATA ANALYTICS & REPORTING AUTOMATION")
    print("=" * 64)

    print(f"\n[1/4] generating {total:,} synthetic transactions (chunked)...")
    generate_transactions(total_rows=total, out_dir=data_dir)

    print("\n[2/4] query optimization showcase")
    optimize_demo(data_dir)

    print("\n[3/4] EDA + customer behavior")
    eda_summary(data_dir)
    customer_behavior(data_dir)

    print("\n[4/4] automated weekly/monthly reports")
    rdir = generate_reports(data_dir)
    print(f"\nDone. Reports in {rdir}/")


if __name__ == "__main__":
    main()
