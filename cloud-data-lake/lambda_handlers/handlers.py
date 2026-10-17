"""
Lambda-like event handlers.

In AWS these respond to S3:ObjectCreated events. Here they are plain
functions invoked by the orchestrator after each lake write — same
event-driven semantics, no cloud required.
"""
import os


def on_bronze_write(root, table, rows):
    """Trigger silver Glue job when bronze data lands."""
    print(f"[lambda:bronze-arrived] table={table} rows={rows:,} "
          f"-> triggering silver clean job")
    from src.glue_jobs import silver_clean
    return silver_clean(root)


def on_silver_write(root, table, rows):
    """Trigger gold aggregation when silver data lands."""
    print(f"[lambda:silver-arrived] table={table} rows={rows:,} "
          f"-> triggering gold aggregate job")
    from src.glue_jobs import gold_aggregate
    return gold_aggregate(root)


def on_gold_write(root, table, rows):
    """Notify/report when gold KPIs refresh."""
    stamp = os.path.join(root, "gold", "_LAST_REFRESH")
    with open(stamp, "w") as f:
        f.write(f"{table}:{rows}")
    print(f"[lambda:gold-arrived] table={table} rows={rows:,} "
          f"-> refresh stamp written; dashboard rebuild triggered")
