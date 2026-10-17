"""
Data-quality suite: nulls, duplicates, inconsistencies.
Runs in lenient mode on raw (expect failures) and strict mode on clean.
"""


def run_quality_suite(df, table, strict=True):
    checks = []
    nulls = int(df.isna().sum().sum())
    checks.append(("no_nulls_in_keys",
                   nulls == 0, f"{nulls} null cells"))
    dupes = int(df.duplicated(subset=["order_id"]).sum()) \
        if "order_id" in df.columns else 0
    checks.append(("no_duplicate_order_id",
                   dupes == 0, f"{dupes} dupes"))
    if "quantity" in df.columns:
        bad_q = int((df["quantity"] <= 0).sum())
        checks.append(("quantity_positive",
                       bad_q == 0, f"{bad_q} non-positive"))
    if "unit_price" in df.columns:
        bad_p = int((df["unit_price"] <= 0).sum())
        checks.append(("unit_price_positive",
                       bad_p == 0, f"{bad_p} non-positive"))
    passed = sum(1 for _, ok, _ in checks if ok)
    print(f"[quality:{table}] {passed}/{len(checks)} checks passed"
          + ("" if passed == len(checks) else "  <-- issues found"))
    for name, ok, detail in checks:
        print(f"    {'PASS' if ok else 'FAIL'}: {name} — {detail}")
    if strict and passed != len(checks):
        raise RuntimeError(f"quality gate FAILED for {table}")
    return {"table": table, "passed": passed, "total": len(checks),
            "checks": checks}
