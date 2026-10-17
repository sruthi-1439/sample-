"""
Automated reporting — generates weekly & monthly summary reports
(the kind of scheduled job that used to be manual Excel work).
"""
import os
import datetime
import pandas as pd
from .analysis import iter_partitions

REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")


def _summarize(data_dir, start, end, label):
    frames = []
    for chunk in iter_partitions(
            data_dir, columns=["txn_date", "amount", "category", "channel"]):
        m = chunk[(chunk["txn_date"] >= start) & (chunk["txn_date"] < end)]
        if len(m):
            frames.append(m)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    by_cat = df.groupby("category")["amount"].agg(["count", "sum"]).round(2)
    by_cat.columns = ["txns", "volume"]
    by_chan = df.groupby("channel")["amount"].sum().round(2)
    return {
        "label": label,
        "txns": len(df),
        "volume": round(df["amount"].sum(), 2),
        "avg_ticket": round(df["amount"].mean(), 2),
        "by_category": by_cat.sort_values("volume", ascending=False),
        "by_channel": by_chan.sort_values(ascending=False),
    }


def _write(summary, path):
    with open(path, "w") as f:
        f.write(f"# Transaction Report — {summary['label']}\n\n")
        f.write(f"- Transactions: {summary['txns']:,}\n")
        f.write(f"- Total volume: ${summary['volume']:,.2f}\n")
        f.write(f"- Avg ticket: ${summary['avg_ticket']:,.2f}\n\n")
        f.write("## Volume by category\n")
        f.write(summary["by_category"].to_string() + "\n\n")
        f.write("## Volume by channel\n")
        f.write(summary["by_channel"].to_string() + "\n")
    print(f"[report] wrote {path}")


def generate_reports(data_dir, ref_date="2024-03-01"):
    os.makedirs(REPORT_DIR, exist_ok=True)
    ref = pd.to_datetime(ref_date)
    week = _summarize(data_dir, ref - pd.Timedelta(days=7), ref,
                      f"week ending {ref.date()}")
    month = _summarize(data_dir, ref - pd.DateOffset(months=1), ref,
                       f"month ending {ref.date()}")
    if week:
        _write(week, os.path.join(REPORT_DIR, "weekly_report.md"))
    if month:
        _write(month, os.path.join(REPORT_DIR, "monthly_report.md"))
    return REPORT_DIR
