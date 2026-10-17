"""
Data validation framework — the quality gate that runs inside every
Glue-like transform job. Each check returns (passed: bool, detail: str).
"""
import pandas as pd


class ValidationReport:
    def __init__(self, table_name):
        self.table_name = table_name
        self.checks = []

    def add(self, name, passed, detail=""):
        self.checks.append({"check": name, "passed": bool(passed),
                            "detail": str(detail)})

    @property
    def passed(self):
        return all(c["passed"] for c in self.checks)

    def summary(self):
        lines = [f"  [{self.table_name}] "
                 f"{sum(c['passed'] for c in self.checks)}/{len(self.checks)} "
                 f"checks passed"]
        for c in self.checks:
            mark = "PASS" if c["passed"] else "FAIL"
            lines.append(f"    {mark}: {c['check']}"
                         + (f" — {c['detail']}" if c["detail"] else ""))
        return "\n".join(lines)


def check_no_nulls(df, columns, report):
    for col in columns:
        n = int(df[col].isna().sum())
        report.add(f"no_nulls:{col}", n == 0, f"{n} nulls")


def check_no_duplicates(df, columns, report):
    n = int(df.duplicated(subset=columns).sum())
    report.add(f"no_duplicates:{columns}", n == 0, f"{n} dupes")


def check_positive(df, column, report):
    bad = int((df[column] <= 0).sum())
    report.add(f"positive:{column}", bad == 0, f"{bad} non-positive")


def check_referential(child, child_col, parent, parent_col, report):
    valid = child[child_col].dropna().isin(parent[parent_col])
    orphans = int((~valid).sum())
    report.add(f"fk:{child_col}->{parent_col}", orphans == 0,
               f"{orphans} orphans")


def check_row_count_bounds(df, lo, hi, report):
    n = len(df)
    report.add("row_count_bounds", lo <= n <= hi, f"{n} rows")
