"""
Data Pipeline Automation & Analytics Dashboard.

Multi-source ETL -> validation report -> Tableau-ready extracts ->
HTML KPI dashboard (mirrors the Tableau view).

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.extract import extract_sales, extract_marketing, extract_support
from src.pipeline import clean_sales, build_marts, validate, write_extracts
from src.dashboard import build_dashboard


def main():
    print("=" * 64)
    print("DATA PIPELINE AUTOMATION & ANALYTICS DASHBOARD")
    print("=" * 64)
    print("\n[1/4] extracting from 3 sources...")
    sales = extract_sales()
    marketing = extract_marketing()
    support = extract_support()
    print(f"  sales: {len(sales):,} | marketing: {len(marketing):,} | "
          f"support: {len(support):,}")

    print("\n[2/4] clean + transform -> marts")
    sales, quarantined = clean_sales(sales)
    print(f"  quarantined {len(quarantined)} rows with null revenue")
    marts = build_marts(sales, marketing, support)

    print("\n[3/4] validation + Tableau extracts")
    ok, _ = validate(sales, marts)
    write_extracts(marts)
    if not ok:
        print("  !! validation issues — see report above")

    print("\n[4/4] KPI dashboard")
    out = os.path.join(os.path.dirname(__file__), "output",
                       "dashboard.html")
    build_dashboard(marts, out)
    print(f"\nDone. Extracts: extracts/ | Dashboard: {out}")


if __name__ == "__main__":
    main()
