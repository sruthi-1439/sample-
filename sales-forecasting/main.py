"""
Sales Forecasting Model.

Seasonal-naive vs ARIMA on synthetic daily sales with trend,
weekly/yearly seasonality, and promo spikes.

Run:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data_gen import generate_sales
from src.models import seasonal_naive, arima_forecast, evaluate

OUT = os.path.join(os.path.dirname(__file__), "output")
HORIZON = 30


def main():
    os.makedirs(OUT, exist_ok=True)
    print("=" * 64)
    print("SALES FORECASTING MODEL")
    print("=" * 64)

    print("\n[1/4] generating 2 years of synthetic daily sales...")
    df = generate_sales()
    train, test = df.iloc[:-HORIZON], df.iloc[-HORIZON:]
    print(f"  train: {len(train)} days | holdout: {len(test)} days")

    print("\n[2/4] fitting models...")
    sn = seasonal_naive(train, HORIZON)
    ar, fit = arima_forecast(train, HORIZON)
    print(f"  ARIMA{fit.model.order} AIC={fit.aic:.0f}")

    print("\n[3/4] evaluating on holdout...")
    scores = evaluate(test, {"seasonal_naive": sn, "arima": ar})
    print(scores.to_string(index=False))
    winner = scores.iloc[0]["model"]
    print(f"  winner: {winner}")

    print("\n[4/4] visualizing + exporting Tableau-ready forecast...")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(train.index[-90:], train["sales"].iloc[-90:],
            label="history (last 90d)", color="gray")
    ax.plot(test.index, test["sales"], label="actual", color="black")
    ax.plot(sn.index, sn.values, label="seasonal naive", linestyle="--")
    ax.plot(ar.index, ar.values, label="ARIMA", linestyle="--")
    ax.set_title("Sales forecast: seasonal-naive vs ARIMA (30-day holdout)")
    ax.set_ylabel("Daily sales ($)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "forecast.png"), dpi=120)
    plt.close(fig)

    fcst_out = test[["sales"]].rename(
        columns={"sales": "actual"}).copy()
    fcst_out["seasonal_naive"] = sn.values
    fcst_out["arima"] = ar.values.round(2)
    fcst_out.to_csv(os.path.join(OUT, "forecast_tableau.csv"))
    print(f"  saved output/forecast.png and output/forecast_tableau.csv")
    print("\nDone.")


if __name__ == "__main__":
    main()
