# Sales Forecasting Model

Compares **seasonal-naive** vs **ARIMA** on synthetic daily sales with
trend, weekly/yearly seasonality, promo spikes, and noise. Evaluated on a
30-day holdout; forecasts exported Tableau-ready.

## Approach

```
synthetic sales (2 yrs daily) ──▶ train/test split ──▶ seasonal-naive
                                                      ──▶ ARIMA(2,1,2)
                                                      ──▶ MAE/MAPE compare
                                                      ──▶ forecast.png + CSV
```

## Why not Prophet?

Prophet was deliberately excluded: it pulls in cmdstanpy and a ~100MB+
Stan toolchain that frequently fails in lightweight and CI environments.
Seasonal-naive + ARIMA gives an honest, reproducible baseline comparison
with zero heavyweight dependencies.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Sample output

```
[2/4] fitting models...
  ARIMA(2, 1, 2) AIC=7989
[3/4] evaluating on holdout...
         model   MAE  MAPE_%
         arima 36.74    5.21
seasonal_naive 43.96    6.15
  winner: arima
```

## Outputs

- `output/forecast.png` — history + actuals + both forecasts
- `output/forecast_tableau.csv` — date, actual, seasonal_naive, arima
  (connect Tableau directly for forecast-vs-actual dashboards)

## Technologies

Python, pandas, NumPy, statsmodels (ARIMA), scikit-learn (metrics),
matplotlib.
