"""
ML models: anomaly detection, cost regression, patient segmentation.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


def _features(df):
    diag = pd.get_dummies(df["diagnosis_code"], prefix="dx", dtype=float)
    plan = pd.get_dummies(df["plan_type"], prefix="plan", dtype=float)
    X = pd.concat([df[["age"]].astype(float), diag, plan], axis=1)
    return X


def detect_anomalies(df):
    """Isolation Forest flags suspicious claims for payment-integrity review."""
    X = _features(df)
    X["claim_amount"] = df["claim_amount"]
    iso = IsolationForest(contamination=0.02, random_state=42)
    df = df.copy()
    df["anomaly_score"] = -iso.fit_predict(X)  # 1 = anomaly
    df["is_anomaly"] = (df["anomaly_score"] == 1).astype(int)
    # How many injected frauds did we catch? (labels exist only in synthetic)
    caught = df.loc[df["is_fraud_injected"], "is_anomaly"].mean()
    print(f"[anomaly] flagged {int(df['is_anomaly'].sum())} anomalous claims; "
          f"recall on injected fraud: {caught:.1%}")
    return df, {"fraud_recall": float(caught)}


def predict_costs(df):
    """Ridge regression predicts claim cost from member + clinical features.

    Trains on adjudicated (non-anomalous) claims only — mirroring how payer
    cost models exclude payment-integrity-flagged claims — with a log
    transform, the standard approach for right-skewed healthcare costs.
    """
    clean = df[df["is_anomaly"] == 0].copy()
    X = _features(clean)
    y = np.log1p(clean["claim_amount"])
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2,
                                          random_state=42)
    model = Ridge(alpha=1.0)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    # Report MAE back on the dollar scale
    mae = mean_absolute_error(np.expm1(yte), np.expm1(pred))
    r2 = r2_score(yte, pred)
    print(f"[regression] claim-cost model (n={len(clean)} clean claims): "
          f"MAE=${mae:,.0f}, R²={r2:.3f} (log-cost scale)")
    return model, {"mae": float(mae), "r2": float(r2)}


def segment_patients(df):
    """K-Means on member-level aggregates -> utilization segments."""
    member = df.groupby("member_id").agg(
        total_cost=("claim_amount", "sum"),
        claim_count=("claim_id", "count"),
        avg_age=("age", "mean")).reset_index()
    Xs = StandardScaler().fit_transform(
        member[["total_cost", "claim_count", "avg_age"]])
    km = KMeans(n_clusters=4, n_init=10, random_state=42)
    member["segment"] = km.fit_predict(Xs)
    profile = member.groupby("segment").agg(
        members=("member_id", "count"),
        avg_cost=("total_cost", "mean"),
        avg_claims=("claim_count", "mean")).round(1)
    print("[segments] patient utilization segments:")
    print(profile.to_string())
    return member, profile
