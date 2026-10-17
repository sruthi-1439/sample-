"""
Cloud-Based Data Lake Integration & Reporting System.

Event-driven pipeline over bronze/silver/gold zones:
  ingest -> [lambda] -> Glue clean -> [lambda] -> Glue aggregate
       -> [lambda] -> Athena queries -> HTML dashboard.

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.lake import lake_root
from src.glue_jobs import bronze_ingest
from lambda_handlers.handlers import (on_bronze_write, on_silver_write,
                                      on_gold_write)
from src.athena import run_athena
from src.reporting import build_dashboard


def main():
    print("=" * 64)
    print("CLOUD DATA LAKE — BRONZE / SILVER / GOLD")
    print("=" * 64)
    root = lake_root()

    print("\n[1/5] bronze ingest (raw events land in the lake)")
    bronze_ingest(root)

    print("\n[2/5] lambda: bronze-arrived -> silver Glue job")
    silver = on_bronze_write(root, "events", 30000)

    print("\n[3/5] lambda: silver-arrived -> gold Glue job")
    gold = on_silver_write(root, "events_clean", len(silver))

    print("\n[4/5] lambda: gold-arrived -> refresh stamp")
    on_gold_write(root, "daily_kpis", len(gold))

    print("\n[5/5] Athena queries + dashboard")
    results = run_athena(root)
    out = os.path.join(os.path.dirname(__file__), "output",
                       "dashboard.html")
    build_dashboard(results, out)
    print(f"\nDone. Open {out} in a browser to view the KPI dashboard.")


if __name__ == "__main__":
    main()
