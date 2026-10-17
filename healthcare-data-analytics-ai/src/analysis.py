"""
SQL analysis layer — runs payer-style analytic queries against SQLite.
Mirrors the kind of claims analysis done in payer data warehouses.
"""
import sqlite3
import pandas as pd

QUERIES = {
    "total_paid_by_plan": """
        SELECT plan_type,
               COUNT(*) AS claims,
               ROUND(SUM(claim_amount), 2) AS total_paid,
               ROUND(AVG(claim_amount), 2) AS avg_claim
        FROM claims GROUP BY plan_type ORDER BY total_paid DESC""",
    "top_diagnoses_by_cost": """
        SELECT diagnosis_code,
               COUNT(*) AS claims,
               ROUND(SUM(claim_amount), 2) AS total_cost
        FROM claims GROUP BY diagnosis_code
        ORDER BY total_cost DESC LIMIT 5""",
    "high_cost_members": """
        SELECT member_id,
               COUNT(*) AS claims,
               ROUND(SUM(claim_amount), 2) AS total_cost
        FROM claims GROUP BY member_id
        HAVING total_cost > 5000
        ORDER BY total_cost DESC LIMIT 10""",
    "monthly_trend": """
        SELECT strftime('%Y-%m', service_date) AS month,
               COUNT(*) AS claims,
               ROUND(SUM(claim_amount), 2) AS total_paid
        FROM claims GROUP BY month ORDER BY month""",
}


def run_sql_analysis(df):
    conn = sqlite3.connect(":memory:")
    df.to_sql("claims", conn, index=False)
    results = {}
    print("[sql] payer claims analysis:")
    for name, sql in QUERIES.items():
        out = pd.read_sql(sql, conn)
        results[name] = out
        print(f"\n  -- {name} --")
        print(out.to_string(index=False))
    conn.close()
    return results
