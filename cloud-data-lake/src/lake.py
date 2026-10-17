"""
S3 data-lake layout: bronze (raw) / silver (cleaned) / gold (aggregated).

In AWS these are S3 prefixes; locally they are folders. The module also
emits a manifest.json per zone, mimicking S3 inventory / Glue catalog
entries.
"""
import os
import json
import pandas as pd

ZONES = ("bronze", "silver", "gold")


def lake_root(base=None):
    root = base or os.path.join(os.path.dirname(__file__), "..", "lake")
    for z in ZONES:
        os.makedirs(os.path.join(root, z), exist_ok=True)
    return root


def write_zone(root, zone, name, df):
    path = os.path.join(root, zone, f"{name}.parquet")
    df.to_parquet(path, index=False)
    manifest = {"table": name, "zone": zone, "rows": len(df),
                "columns": list(df.columns),
                "s3_uri": f"s3://data-lake/{zone}/{name}.parquet"}
    with open(os.path.join(root, zone, f"{name}.manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[lake] {zone}/{name}: {len(df):,} rows -> {path}")
    return path


def read_zone(root, zone, name, columns=None):
    return pd.read_parquet(os.path.join(root, zone, f"{name}.parquet"),
                           columns=columns)
