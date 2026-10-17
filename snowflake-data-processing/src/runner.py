"""
SQL runner: executes the Snowflake-dialect analytics on local data.

Snowflake SQL in sql/*.sql is the source of truth for production.
This runner ports the same logic to SQLite (translating DATE_TRUNC,
STDDEV, TRY_CAST) so the analytics are verifiable without a warehouse.
"""
import sqlite3
import pandas as pd

SQLITE_LTV = """
WITH clean_orders AS (
    SELECT order_id, customer_id,
           date(order_date) AS order_date,
           quantity, unit_price,
           quantity * unit_price AS line_total
    FROM raw_orders
    WHERE quantity > 0 AND unit_price > 0 AND customer_id IS NOT NULL
),
customer_monthly AS (
    SELECT customer_id,
           substr(order_date, 1, 7) AS order_month,
           COUNT(*) AS orders,
           SUM(line_total) AS revenue
    FROM clean_orders GROUP BY customer_id, order_month
)
SELECT customer_id, order_month, orders, ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (
           PARTITION BY customer_id ORDER BY order_month
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2)
           AS lifetime_revenue,
       RANK() OVER (
           PARTITION BY order_month ORDER BY revenue DESC)
           AS revenue_rank_in_month,
       ROUND(AVG(revenue) OVER (
           PARTITION BY customer_id ORDER BY order_month
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)
           AS rolling_3mo_avg_revenue
FROM customer_monthly ORDER BY customer_id, order_month
"""

SQLITE_ANOMALY = """
WITH product_stats AS (
    SELECT product_id,
           AVG(quantity * unit_price) AS avg_line_total
    FROM raw_orders WHERE quantity > 0 AND unit_price > 0
    GROUP BY product_id
),
flagged AS (
    SELECT o.order_id, o.customer_id, o.product_id,
           o.quantity * o.unit_price AS line_total,
           s.avg_line_total
    FROM raw_orders o JOIN product_stats s USING (product_id)
    WHERE o.quantity > 0 AND o.unit_price > 0
)
SELECT order_id, customer_id, product_id,
       ROUND(line_total, 2) AS line_total
FROM flagged
WHERE line_total > 3 * avg_line_total
ORDER BY line_total DESC LIMIT 10
"""


def run_sql_suite(clean_orders):
    conn = sqlite3.connect(":memory:")
    raw = clean_orders.drop(columns=["line_total", "order_month"],
                            errors="ignore")
    raw.to_sql("raw_orders", conn, index=False)
    ltv = pd.read_sql(SQLITE_LTV, conn)
    anom = pd.read_sql(SQLITE_ANOMALY, conn)
    conn.close()
    print("[sql] customer lifetime value (window functions) — head:")
    print(ltv.head(8).to_string(index=False))
    print(f"  ... {len(ltv):,} customer-month rows")
    print("[sql] anomaly scan — largest outliers vs product norm:")
    print(anom.to_string(index=False) if len(anom) else "  none flagged")
    return ltv, anom
