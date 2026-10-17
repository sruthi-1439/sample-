"""
HTML dashboard mimicking the Tableau KPI view: revenue trend, ROAS,
regional mix, CSAT — rendered as static HTML with inline SVG bars.
"""
import os
import pandas as pd


def _bars(df, label_col, val_col, width=240, money=False):
    mx = df[val_col].max() or 1
    out = []
    for _, r in df.iterrows():
        w = int(width * r[val_col] / mx)
        v = f"${r[val_col]:,.0f}" if money else f"{r[val_col]:,.1f}"
        out.append(f"<div class='row'><span class='lbl'>{r[label_col]}</span>"
                   f"<span class='bar' style='width:{w}px'></span>"
                   f"<span class='val'>{v}</span></div>")
    return "".join(out)


def build_dashboard(marts, out_path):
    sales = marts["sales_mart"]
    roas = marts["roas"]
    csat = marts["csat_mart"]

    rev_trend = sales.groupby("month")["revenue"].sum().reset_index()
    rev_by_region = sales.groupby("region")["revenue"].sum().reset_index()
    csat_by_region = csat.groupby("region")["avg_csat"].mean().reset_index()
    kpi_rev = sales["revenue"].sum()
    kpi_roas = (sales["revenue"].sum() /
                marts["spend_mart"]["spend"].sum())
    kpi_csat = csat["avg_csat"].mean()

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Sales Analytics Dashboard</title>
<style>
body{{font-family:Arial,sans-serif;max-width:900px;margin:2em auto;color:#222}}
h1{{border-bottom:3px solid #1f4e79;padding-bottom:.3em}}
h2{{color:#1f4e79;margin-top:1.5em}}
.cards{{display:flex;gap:1em}}
.card{{flex:1;background:#eef3f8;border-radius:8px;padding:1em;text-align:center}}
.card b{{font-size:1.7em;display:block;color:#1f4e79}}
.row{{display:flex;align-items:center;gap:.5em;margin:.25em 0}}
.lbl{{width:80px;font-size:.9em}}
.bar{{height:14px;background:#2e75b6;border-radius:3px}}
.val{{font-size:.85em;color:#555}}
</style></head><body>
<h1>&#128200; Sales Analytics Dashboard</h1>
<div class="cards">
<div class="card"><b>${kpi_rev:,.0f}</b>total revenue</div>
<div class="card"><b>{kpi_roas:.2f}x</b>blended ROAS</div>
<div class="card"><b>{kpi_csat:.2f}/5</b>avg CSAT</div>
</div>
<h2>Monthly revenue trend</h2>{_bars(rev_trend, "month", "revenue", money=True)}
<h2>Revenue by region</h2>{_bars(rev_by_region, "region", "revenue", money=True)}
<h2>Monthly ROAS</h2>{_bars(roas, "month", "roas")}
<h2>Avg CSAT by region</h2>{_bars(csat_by_region, "region", "avg_csat")}
<p><em>KPIs mirror the Tableau dashboard; source extracts in extracts/</em></p>
</body></html>"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"[dashboard] -> {out_path}")
