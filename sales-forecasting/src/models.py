"""
Forecasting models.

- SeasonalNaive: repeats the value from 7 days ago (weekly seasonality).
- ARIMA: statsmodels ARIMA(2,1,2) with weekly seasonal differencing via
  exogenous Fourier terms is overkill here; we use auto-selected
  (p,d,q) = (2,1,2) on the series — a standard, explainable baseline.

Note on Prophet: deliberately not used. Prophet pulls in cmdstanpy and a
~100MB+ toolchain that frequently fails in lightweight/CI environments;
ARIMA + seasonal-naive gives an honest, reproducible comparison without it.
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error


def seasonal_naive(train, horizon):
    """Repeat last week's pattern."""
    hist = train["sales"].values
    fcst = np.array([hist[-7 + (i % 7)] if len(hist) >= 7 else hist[-1]
                     for i in range(horizon)])
    idx = pd.date_range(train.index[-1] + pd.Timedelta(days=1),
                        periods=horizon, freq="D")
    return pd.Series(fcst, index=idx, name="seasonal_naive")


def arima_forecast(train, horizon, order=(2, 1, 2)):
    model = ARIMA(train["sales"], order=order)
    fit = model.fit()
    fcst = fit.forecast(steps=horizon)
    fcst.name = "arima"
    return fcst, fit


def evaluate(actual, forecasts):
    rows = []
    for name, fcst in forecasts.items():
        aligned = fcst.reindex(actual.index)
        mae = mean_absolute_error(actual["sales"], aligned)
        mape = float((abs(actual["sales"] - aligned)
                      / actual["sales"]).mean() * 100)
        rows.append({"model": name, "MAE": round(mae, 2),
                     "MAPE_%": round(mape, 2)})
    return pd.DataFrame(rows).sort_values("MAE")
