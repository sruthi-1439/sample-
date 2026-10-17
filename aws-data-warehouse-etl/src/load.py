"""
Load stage — simulates Redshift.

In AWS, curated Parquet in S3 would be COPY'd into Amazon Redshift
fact/dimension tables. Locally we load into SQLite (same star-schema
shape, SQL-verifiable) at warehouse/analytics.db.
"""
import os
import sqlite3
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "data_lake")
CURATED = os.path.join(BASE, "curated")
WAREHOUSE = os.path.join(os.path.dirname(__file__), "..", "warehouse")


def load_to_warehouse():
    os.makedirs(WAREHOUSE, exist_ok=True)
    db_path = os.path.join(WAREHOUSE, "analytics.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)

    tables = {}
    for name in ["dim_customers", "dim_products", "fact_orders"]:
        df = pd.read_parquet(os.path.join(CURATED, f"{name}.parquet"))
        df.to_sql(name, conn, index=False)
        tables[name] = len(df)

    # Sanity: sample analytic query against the "warehouse"
    sample = pd.read_sql(
        """SELECT c.region,
                  COUNT(*) AS orders,
                  ROUND(SUM(f.line_total), 2) AS revenue
           FROM fact_orders f
           JOIN dim_customers c ON f.customer_id = c.customer_id
           WHERE f.status = 'completed'
           GROUP BY c.region
           ORDER BY revenue DESC""", conn)
    conn.close()
    print(f"[load] warehouse ready at {db_path}: {tables}")
    print("[load] sample mart query — revenue by region (completed orders):")
    print(sample.to_string(index=False))
    return db_path
