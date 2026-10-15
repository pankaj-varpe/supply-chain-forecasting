"""Inventory policy parameters. All inputs come from BEFORE the test year."""
import numpy as np
import pandas as pd
from scipy.stats import norm


def policy_params(val_fc, dim_item, service_level):
    """val_fc: hold-out forecasts (store, item, week_start, actual, forecast).
    Returns one row per store-item with sigma, safety stock and EOQ."""
    d = val_fc.assign(err=val_fc["forecast"] - val_fc["actual"])
    g = d.groupby(["store", "item"]).agg(
        sigma_week=("err", lambda x: x.std(ddof=1)),   # weekly forecast-error std
        bias_week=("err", "mean"),
        annual_demand=("actual", "sum"),               # last full pre-test year
    ).reset_index()

    p = g.merge(dim_item, on="item")
    for c in ["unit_cost", "holding_cost_rate", "order_cost", "lead_time_days"]:
        p[c] = p[c].astype(float)

    z = norm.ppf(service_level)                        # 0.95 -> about 1.645
    # sigma is per WEEK, lead time is in DAYS -> convert days to weeks
    p["safety_stock"] = z * p["sigma_week"] * np.sqrt(p["lead_time_days"] / 7)
    # EOQ = sqrt(2 * D * S / H), H = holding cost per unit per year
    p["eoq"] = np.sqrt(2 * p["annual_demand"] * p["order_cost"]
                       / (p["holding_cost_rate"] * p["unit_cost"]))
    return p


def reorder_point(weekly_forecast, lead_time_days, safety_stock):
    """Mean demand over the lead time (forecast rate per day x days) + safety stock."""
    return weekly_forecast / 7 * lead_time_days + safety_stock