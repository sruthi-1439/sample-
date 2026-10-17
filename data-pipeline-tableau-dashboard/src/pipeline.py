"""
Clean / transform / validate, then emit Tableau-ready extracts.

Tableau Hyper extracts need the Tableau Hyper API; to keep this project
dependency-light we emit optimized CSV extracts (Tableau connects natively)
plus a data dictionary — the same grain Tableau would consume.
"""
import os
import pandas as pd

EXTRACT_DIR = os.path.join(os.path.dirname(__file__), "..", "extracts")


def clean_sales(df):
    q = df[df["revenue"].isna()]
    clean = df.dropna(subset=["revenue"]).copy()
    clean["date"] = pd.to_datetime(clean["date"])
    return clean, q


def build_marts(sales, marketing, support):
    sales["month"] = sales["date"].dt.strftime("%Y-%m")
    marketing["month"] = pd.to_datetime(marketing["date"]).dt.strftime(
        "%Y-%m")
    support["month"] = support["date"].dt.strftime("%Y-%m")

    sales_mart = (sales.groupby(["month", "region", "product"])
                  .agg(units=("units", "sum"),
                       revenue=("revenue", "sum"),
                       orders=("sale_id", "count")).reset_index())
    spend_mart = (marketing.groupby(["month", "channel"])
                  .agg(spend=("spend", "sum"),
                       impressions=("impressions", "sum")).reset_index())
    # ROAS per month (marketing efficiency KPI for the dashboard)
    rev = sales_mart.groupby("month")["revenue"].sum()
    sp = spend_mart.groupby("month")["spend"].sum()
    roas = (rev / sp).rename("roas").reset_index()
    csat_mart = (support.groupby(["month", "region"])
                 .agg(tickets=("ticket_id", "count"),
                      avg_csat=("csat", "mean"),
                      avg_resolution_hrs=("resolution_hours", "mean"))
                 .round(2).reset_index())
    return {"sales_mart": sales_mart, "spend_mart": spend_mart,
            "roas": roas, "csat_mart": csat_mart}


def validate(sales, marts):
    report = []
    nulls = int(sales["revenue"].isna().sum())
    report.append(("sales.revenue no nulls", nulls == 0, f"{nulls} nulls"))
    dupes = int(sales.duplicated(subset=["sale_id"]).sum())
    report.append(("sales.sale_id unique", dupes == 0, f"{dupes} dupes"))
    neg = int((marts["sales_mart"]["revenue"] < 0).sum())
    report.append(("marts revenue non-negative", neg == 0, f"{neg} rows"))
    for m in marts.values():
        report.append((f"mart rows>0", len(m) > 0, f"{len(m)} rows"))
        break
    ok = all(r[1] for r in report)
    lines = ["[validation] Tableau extract quality report:"]
    for name, passed, detail in report:
        lines.append(f"  {'PASS' if passed else 'FAIL'}: {name} — {detail}")
    print("\n".join(lines))
    return ok, report


def write_extracts(marts):
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    paths = {}
    for name, df in marts.items():
        p = os.path.join(EXTRACT_DIR, f"{name}.csv")
        df.to_csv(p, index=False)
        paths[name] = p
    # data dictionary for Tableau field mapping
    dd = pd.DataFrame([
        ("sales_mart", "month", "YYYY-MM order month"),
        ("sales_mart", "region", "sales region"),
        ("sales_mart", "product", "product name"),
        ("sales_mart", "revenue", "sum of revenue"),
        ("spend_mart", "channel", "marketing channel"),
        ("spend_mart", "spend", "media spend"),
        ("roas", "roas", "revenue / spend"),
        ("csat_mart", "avg_csat", "1-5 satisfaction score"),
    ], columns=["extract", "field", "description"])
    dd.to_csv(os.path.join(EXTRACT_DIR, "_data_dictionary.csv"), index=False)
    print(f"[extracts] {len(paths)} Tableau-ready CSVs -> {EXTRACT_DIR}/")
    return paths
