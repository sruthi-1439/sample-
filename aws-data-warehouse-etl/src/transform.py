"""
Transform stage — Glue-like ETL jobs.

In AWS these would be AWS Glue PySpark jobs reading from S3 and writing
Parquet back to S3 (curated zone). Locally they are pandas jobs reading
CSV from data_lake/raw/ and writing cleaned Parquet to data_lake/curated/.
Each job runs the validation framework and quarantines bad rows.
"""
import os
import pandas as pd
from .validation import (ValidationReport, check_no_nulls, check_no_duplicates,
                         check_positive, check_referential,
                         check_row_count_bounds)

BASE = os.path.join(os.path.dirname(__file__), "..", "data_lake")
RAW = os.path.join(BASE, "raw")
CURATED = os.path.join(BASE, "curated")
QUARANTINE = os.path.join(BASE, "quarantine")


def _load_raw(name):
    return pd.read_csv(os.path.join(RAW, f"{name}.csv"))


def _save(df, name):
    os.makedirs(CURATED, exist_ok=True)
    path = os.path.join(CURATED, f"{name}.parquet")
    df.to_parquet(path, index=False)
    return path


def _quarantine(df, name):
    os.makedirs(QUARANTINE, exist_ok=True)
    path = os.path.join(QUARANTINE, f"{name}_quarantine.csv")
    df.to_csv(path, index=False)
    return path


def job_clean_customers():
    """Glue job 1: standardize customers, drop invalid emails."""
    df = _load_raw("customers")
    report = ValidationReport("customers_raw")
    check_no_nulls(df, ["customer_id", "email"], report)
    check_no_duplicates(df, ["customer_id"], report)

    bad_email = ~df["email"].str.contains("@", na=False)
    if bad_email.any():
        _quarantine(df[bad_email], "customers")
    clean = df[~bad_email].copy()
    clean["email"] = clean["email"].str.lower().str.strip()
    clean["signup_date"] = pd.to_datetime(clean["signup_date"])

    out = ValidationReport("customers_curated")
    check_no_nulls(clean, ["customer_id", "email"], out)
    check_no_duplicates(clean, ["customer_id"], out)
    check_row_count_bounds(clean, 1000, 10000, out)
    _save(clean, "dim_customers")
    return clean, report, out


def job_clean_products():
    """Glue job 2: fix negative prices, quarantine them."""
    df = _load_raw("products")
    report = ValidationReport("products_raw")
    check_positive(df, "unit_price", report)

    bad = df["unit_price"] <= 0
    if bad.any():
        _quarantine(df[bad], "products")
    clean = df[~bad].copy()
    clean["category"] = clean["category"].str.strip()

    out = ValidationReport("products_curated")
    check_no_nulls(clean, ["product_id", "unit_price"], out)
    check_no_duplicates(clean, ["product_id"], out)
    check_positive(clean, "unit_price", out)
    _save(clean, "dim_products")
    return clean, report, out


def job_build_orders(customers, products):
    """Glue job 3: clean orders, enforce FKs, derive line totals."""
    df = _load_raw("orders")
    report = ValidationReport("orders_raw")
    check_no_nulls(df, ["order_id"], report)
    check_no_duplicates(df, ["order_id"], report)

    # Drop null-FK rows and exact duplicates into quarantine
    mask_null_fk = df["customer_id"].isna() | df["product_id"].isna()
    mask_dupe = df.duplicated(subset=["order_id"], keep="first")
    quarantined = df[mask_null_fk | mask_dupe]
    if len(quarantined):
        _quarantine(quarantined, "orders")
    clean = df[~(mask_null_fk | mask_dupe)].copy()
    clean["customer_id"] = clean["customer_id"].astype(int)
    clean["product_id"] = clean["product_id"].astype(int)
    clean["order_date"] = pd.to_datetime(clean["order_date"])

    # Enrich with unit price -> line total (fact table grain: order line)
    clean = clean.merge(products[["product_id", "unit_price"]],
                        on="product_id", how="left")
    # Quarantine rows whose product FK no longer resolves (e.g. product was
    # quarantined upstream for a negative price) — keeps the fact table clean.
    orphan_fk = clean["unit_price"].isna()
    if orphan_fk.any():
        _quarantine(clean[orphan_fk].drop(columns=["unit_price"]),
                    "orders_orphan_fk")
        clean = clean[~orphan_fk].copy()
    clean["line_total"] = (clean["quantity"] * clean["unit_price"]).round(2)

    out = ValidationReport("fact_orders_curated")
    check_no_nulls(clean, ["order_id", "customer_id", "product_id",
                           "line_total"], out)
    check_no_duplicates(clean, ["order_id"], out)
    check_referential(clean, "customer_id", customers, "customer_id", out)
    check_referential(clean, "product_id", products, "product_id", out)
    check_positive(clean, "line_total", out)
    _save(clean, "fact_orders")
    return clean, report, out


def run_all_transforms():
    customers, r1a, r1b = job_clean_customers()
    products, r2a, r2b = job_clean_products()
    orders, r3a, r3b = job_build_orders(customers, products)
    reports = [r1a, r1b, r2a, r2b, r3a, r3b]
    print("[transform] validation results:")
    for r in reports:
        print(r.summary())
    return {"customers": customers, "products": products, "orders": orders}, \
        reports
