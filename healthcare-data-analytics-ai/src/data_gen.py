"""
Synthetic healthcare payer/claims data generator.

All data is fictional and generated with fixed seeds — no real PHI.
"""
import numpy as np
import pandas as pd

DIAGNOSES = ["J06.9", "I10", "E11.9", "M54.5", "F32.9",
             "K21.9", "N39.0", "R50.9", "Z00.00", "G43.909"]
PROVIDERS = [f"PRV{i:04d}" for i in range(1, 51)]
PLANS = ["PPO", "HMO", "HDHP", "EPO"]


def generate_claims(n=10000, seed=42):
    rng = np.random.default_rng(seed)
    member_ids = rng.integers(1, 4001, size=n)
    ages = rng.integers(18, 90, size=n)
    diagnoses = rng.choice(DIAGNOSES, size=n)
    providers = rng.choice(PROVIDERS, size=n)
    plans = rng.choice(PLANS, size=n, p=[0.4, 0.3, 0.2, 0.1])

    # Claim cost: base by diagnosis + age effect + noise
    base = {"J06.9": 180, "I10": 320, "E11.9": 450, "M54.5": 600,
            "F32.9": 380, "K21.9": 250, "N39.0": 300, "R50.9": 150,
            "Z00.00": 120, "G43.909": 280}
    base_cost = np.array([base[d] for d in diagnoses])
    age_effect = (ages - 18) * 4.5
    noise = rng.normal(0, 120, size=n)
    claim_amount = np.maximum(20, base_cost + age_effect + noise).round(2)

    # Inject anomalies: a few extreme fraudulent-looking claims
    fraud_idx = rng.choice(n, size=60, replace=False)
    claim_amount[fraud_idx] *= rng.uniform(8, 15, size=60)

    df = pd.DataFrame({
        "claim_id": np.arange(1, n + 1),
        "member_id": member_ids,
        "age": ages,
        "gender": rng.choice(["M", "F"], size=n),
        "diagnosis_code": diagnoses,
        "provider_id": providers,
        "plan_type": plans,
        "claim_amount": np.round(claim_amount, 2),
        "service_date": pd.to_datetime("2024-01-01") + pd.to_timedelta(
            rng.integers(0, 365, size=n), unit="D"),
        "is_fraud_injected": False,
    })
    df.loc[fraud_idx, "is_fraud_injected"] = True
    return df
