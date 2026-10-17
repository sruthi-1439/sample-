-- Snowflake-dialect analytics: customer lifetime value with window functions.
-- CTEs build clean marts; window functions rank and accumulate.
-- The Python runner (src/runner.py) executes the equivalent logic on SQLite.

WITH clean_orders AS (
    SELECT
        order_id,
        customer_id,
        TRY_CAST(order_date AS DATE) AS order_date,
        quantity,
        unit_price,
        quantity * unit_price AS line_total
    FROM raw_orders
    WHERE quantity > 0
      AND unit_price > 0
      AND customer_id IS NOT NULL
),
customer_monthly AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', order_date) AS order_month,
        COUNT(*) AS orders,
        SUM(line_total) AS revenue
    FROM clean_orders
    GROUP BY customer_id, order_month
)
SELECT
    customer_id,
    order_month,
    orders,
    revenue,
    SUM(revenue) OVER (
        PARTITION BY customer_id
        ORDER BY order_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS lifetime_revenue,
    RANK() OVER (
        PARTITION BY order_month
        ORDER BY revenue DESC
    ) AS revenue_rank_in_month,
    AVG(revenue) OVER (
        PARTITION BY customer_id
        ORDER BY order_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_3mo_avg_revenue
FROM customer_monthly
ORDER BY customer_id, order_month;
