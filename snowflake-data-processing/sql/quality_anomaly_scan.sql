-- Snowflake-dialect: data-quality anomaly scan with joins + CTEs.
-- Flags orders whose line total deviates wildly from the product norm.

WITH product_stats AS (
    SELECT
        product_id,
        AVG(quantity * unit_price) AS avg_line_total,
        STDDEV(quantity * unit_price) AS std_line_total
    FROM raw_orders
    WHERE quantity > 0 AND unit_price > 0
    GROUP BY product_id
),
flagged AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.product_id,
        o.quantity * o.unit_price AS line_total,
        s.avg_line_total,
        (o.quantity * o.unit_price - s.avg_line_total)
            / NULLIF(s.std_line_total, 0) AS z_score
    FROM raw_orders o
    JOIN product_stats s USING (product_id)
    WHERE o.quantity > 0 AND o.unit_price > 0
)
SELECT order_id, customer_id, product_id,
       ROUND(line_total, 2) AS line_total,
       ROUND(z_score, 2) AS z_score
FROM flagged
WHERE ABS(z_score) > 3
ORDER BY ABS(z_score) DESC
LIMIT 50;
