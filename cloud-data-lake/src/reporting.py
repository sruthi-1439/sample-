"""
Reporting module — builds a KPI dashboard as a self-contained HTML file.

In AWS this would be QuickSight; here we render the same KPIs
(events, users, revenue, funnel, daily trend) as static HTML with
inline SVG bar charts — no JS dependencies, opens in any browser.
"""
import os


def _bar(label, value, max_value, width=220):
    w = int(width * value / max_value) if max_value else 0
    return (f"<div class='row'><span class='lbl'>{label}</span>"
            f"<span class='bar' style='width:{w}px'></span>"
            f"<span class='val'>{value:,.0f}</span></div>")


def build_dashboard(results, out_path):
    kpi = results["kpi_overview"].iloc[0]
    funnel = results["funnel"]
    by_country = results["revenue_by_country"]
    trend = results["daily_trend"].tail(14)

    fmax = funnel["events"].max()
    funnel_html = "".join(
        _bar(r["event_type"], r["events"], fmax) for _, r in funnel.iterrows())
    cmax = by_country["total_revenue"].max()
    country_html = "".join(
        _bar(r["country"], r["total_revenue"], cmax)
        for _, r in by_country.iterrows())
    tmax = trend["revenue"].max()
    trend_html = "".join(
        _bar(r["event_date"], r["revenue"], tmax) for _, r in trend.iterrows())

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Lake KPI Dashboard</title>
<style>
body{{font-family:Arial,sans-serif;max-width:900px;margin:2em auto;color:#222}}
h1{{border-bottom:3px solid #232f3e;padding-bottom:.3em}}
h2{{color:#232f3e;margin-top:1.5em}}
.cards{{display:flex;gap:1em}}
.card{{flex:1;background:#f5f7fa;border-radius:8px;padding:1em;text-align:center}}
.card b{{font-size:1.8em;display:block;color:#ff9900}}
.row{{display:flex;align-items:center;gap:.5em;margin:.25em 0}}
.lbl{{width:90px;font-size:.9em}}
.bar{{height:14px;background:#ff9900;border-radius:3px}}
.val{{font-size:.85em;color:#555}}
</style></head><body>
<h1>&#128202; Data Lake KPI Dashboard</h1>
<div class="cards">
<div class="card"><b>{kpi['events']:,.0f}</b>events</div>
<div class="card"><b>{kpi['users']:,.0f}</b>users</div>
<div class="card"><b>${kpi['revenue']:,.0f}</b>revenue</div>
</div>
<h2>Event funnel</h2>{funnel_html}
<h2>Revenue by country</h2>{country_html}
<h2>Daily revenue (last 14 days)</h2>{trend_html}
<p><em>Generated from the gold zone by the reporting module.</em></p>
</body></html>"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"[report] dashboard -> {out_path}")
    return out_path
