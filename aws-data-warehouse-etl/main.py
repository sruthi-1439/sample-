"""
AWS Cloud Data Warehouse & ETL Automation (local simulation).

Pipeline:  extract (sources -> S3 raw) -> transform (Glue jobs -> S3 curated)
        -> load (Redshift warehouse)  with validation gates at each step.

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.extract import extract_all
from src.transform import run_all_transforms
from src.load import load_to_warehouse


def main():
    print("=" * 64)
    print("AWS DATA WAREHOUSE ETL — local simulation")
    print("=" * 64)
    print("\n[1/3] EXTRACT  (sources -> s3://raw)")
    extract_all()
    print("\n[2/3] TRANSFORM  (Glue jobs -> s3://curated, with QC gates)")
    _, reports = run_all_transforms()
    failed = [r.table_name for r in reports if not r.passed]
    if failed:
        print(f"\n!! validation FAILED for: {failed} "
              f"(bad rows quarantined, see data_lake/quarantine/)")
    else:
        print("\nall validation gates passed ✔")
    print("\n[3/3] LOAD  (S3 curated -> Redshift)")
    db_path = load_to_warehouse()
    print(f"\nDone. Warehouse: {db_path}")


if __name__ == "__main__":
    main()
