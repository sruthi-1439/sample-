"""
Detection: unsupervised Isolation Forest + supervised classifier,
evaluated against the injected fraud labels (synthetic ground truth).
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report, roc_auc_score,
                             confusion_matrix)

FEATURE_COLS = ["clicks", "unique_apps", "app_entropy", "median_gap_s",
                "gap_cv", "night_share"]


def unsupervised(feat):
    X = feat[FEATURE_COLS]
    iso = IsolationForest(contamination=0.05, random_state=42)
    feat = feat.copy()
    feat["iso_anomaly"] = (iso.fit_predict(X) == -1).astype(int)
    return feat


def supervised(feat):
    X = feat[FEATURE_COLS]
    y = (feat["fraud_rate"] > 0.5).astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3,
                                          random_state=42,
                                          stratify=y)
    clf = RandomForestClassifier(n_estimators=200, random_state=42,
                                 n_jobs=-1)
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xte)
    proba = clf.predict_proba(Xte)[:, 1]
    print("[supervised] RandomForest on IP features:")
    print(classification_report(yte, pred, digits=3,
                                target_names=["legit", "fraud"]))
    auc = roc_auc_score(yte, proba)
    print(f"  ROC-AUC: {auc:.3f}")
    feat = feat.copy()
    feat["rf_fraud_proba"] = clf.predict_proba(X)[:, 1]
    importances = pd.Series(clf.feature_importances_,
                            index=FEATURE_COLS).sort_values(ascending=False)
    print("  feature importances:")
    print(importances.to_string())
    return feat, {"roc_auc": float(auc),
                  "report": classification_report(yte, pred,
                                                 output_dict=True)}
