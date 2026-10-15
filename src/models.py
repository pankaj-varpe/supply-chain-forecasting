"""Forecasting models. Every model takes the feature table (pandas) and
returns a DataFrame: store, item, week_start, actual, forecast (test rows only).
To add a model: write one function and add it to MODELS at the bottom."""
import lightgbm as lgb
import numpy as np
import pandas as pd

KEYS = ["store", "item", "week_start"]
# Features known BEFORE the forecast week starts (no leakage)
FEATURES = ["lag_1", "lag_2", "lag_4", "lag_52", "roll4_mean", "roll13_mean",
            "week_of_year", "month_num", "store", "item"]


def _out(test, forecast):
    out = test[KEYS + ["units"]].rename(columns={"units": "actual"}).copy()
    out["forecast"] = np.asarray(forecast, dtype=float)
    return out


def naive(train, test):
    """Forecast = last week's sales."""
    return _out(test, test["lag_1"])


def seasonal_naive(train, test):
    """Forecast = same week last year."""
    return _out(test, test["lag_52"])


def moving_avg(train, test):
    """Forecast = mean of the previous 4 weeks."""
    return _out(test, test["roll4_mean"])


def lightgbm_model(train, test):
    """One global model for all 500 series, trained on training rows only."""
    params = dict(n_estimators=500, learning_rate=0.05, num_leaves=31,
                  min_child_samples=20, random_state=42, verbose=-1)
    model = lgb.LGBMRegressor(**params)
    # store and item as categories so the model does not treat them as ordered numbers
    X_tr, X_te = train[FEATURES].copy(), test[FEATURES].copy()
    for c in ["store", "item"]:
        X_tr[c] = X_tr[c].astype("category")
        X_te[c] = pd.Categorical(X_te[c], categories=X_tr[c].cat.categories)
    model.fit(X_tr, train["units"])
    return _out(test, model.predict(X_te))


MODELS = {"naive": naive, "seasonal_naive": seasonal_naive,
          "moving_avg": moving_avg, "lightgbm": lightgbm_model}


def metrics(df):
    """WMAPE is the main metric: sum of absolute errors / sum of actuals.
    It is not distorted by small actuals the way MAPE is."""
    err = df["forecast"] - df["actual"]
    nz = df["actual"] != 0
    return {
        "WMAPE": err.abs().sum() / df["actual"].sum(),
        "MAPE": (err[nz].abs() / df.loc[nz, "actual"]).mean(),
        "RMSE": float(np.sqrt((err ** 2).mean())),
        "Bias": err.sum() / df["actual"].sum(),   # positive = over-forecasting
    }