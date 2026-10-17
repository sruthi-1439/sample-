"""
Athena-like SQL over the lake, powered by DuckDB.

In AWS, Athena queries S3 Parquet directly with Presto/Trino SQL.
DuckDB gives the same experience locally: SQL over Parquet files,
no server, no warehouse to manage.
"""
import os
import duckdb
import pandas as pd

QUERIES = {
    "kpi_overview": """
        SELECT COUNT(*) AS events,
               COUNT(DISTINCT user_id) AS users,
               ROUND(SUM(amount), 2) AS revenue
        FROM read_parquet('{root}/silver/events_clean.parquet')""",
    "revenue_by_country": """
        SELECT country,
               COUNT(*) AS events,
               ROUND(SUM(revenue), 2) AS total_revenue
        FROM read_parquet('{root}/gold/daily_kpis.parquet')
        GROUP BY country ORDER BY total_revenue DESC""",
    "funnel": """
        SELECT event_type,
               COUNT(*) AS events,
               COUNT(DISTINCT user_id) AS users
        FROM read_parquet('{root}/silver/events_clean.parquet')
        GROUP BY event_type ORDER BY events DESC""",
    "daily_trend": """
        SELECT event_date,
               SUM(events) AS events,
               ROUND(SUM(revenue), 2) AS revenue
        FROM read_parquet('{root}/gold/daily_kpis.parquet')
        GROUP BY event_date ORDER BY event_date""",
}


def run_athena(root):
    con = duckdb.connect()
    results = {}
    print("[athena] querying the lake with DuckDB:")
    for name, tmpl in QUERIES.items():
        sql = tmpl.format(root=root.replace(os.sep, "/"))
        df = con.execute(sql).fetchdf()
        results[name] = df
        print(f"\n  -- {name} --")
        print(df.to_string(index=False))
    con.close()
    return results
