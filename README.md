# Demand Forecasting and Inventory Optimisation (Python + MySQL)

Weekly demand forecasts per store and item, turned into safety stock and reorder points, then tested in a 12-month daily inventory simulation against a naive policy.

## Problem
Can a forecast-based inventory policy reduce stock-outs and total cost compared with the rule "order what sold last week"?

## Data
Kaggle *Store Item Demand Forecasting Challenge*: 913,000 daily rows, 10 stores, 50 items (500 series), 2013-01-01 to 2017-12-31. The file is not included in this repo (licence). Place `train.csv` in `data/`.

## Assumptions (the dataset has no costs, prices or lead times)
- Unit price EUR 1-10, unit cost 50-70% of price, lead time 3-14 days, order cost EUR 20-50, holding cost 20% per year, all random with seed 42 (`src/config.py`).
- **All cost results are therefore illustrative, not real-world savings.**
- Training weeks: 2013-01-07 to 2017-01-01 (208 weeks); test: 2017-01-02 to 2017-12-31 (52 weeks). Weeks run Monday to Sunday.
- ABC thresholds 80% / 95% of cumulative revenue (training data only). XYZ classes are **relative**: tertiles of the coefficient of variation of weekly demand, because the CV range was narrow (about 0.20 to 0.25).
- Forecast horizon: **1 week ahead** (uses last week's actual sales).
- Safety stock = z x sigma_week x sqrt(lead time days / 7), with z = 1.645 (95% target). Sigma is per series, from a 2016 hold-out year (model trained on 2013-2015), so the test year is never used. Weekly errors are assumed independent.
- Simulation: daily, 364 days, unmet demand is lost, fixed lead time, (s, Q) policy with EOQ, start stock = one EOQ. Stock-out cost = lost margin x 1.0 (assumed, tested below).

## Method
1. SQL: ABC/XYZ segmentation, weekly feature table (lags 1, 2, 4, 52; rolling means; calendar), leakage-tested.
2. Models: naive, seasonal naive, 4-week moving average, LightGBM (one global model). Time-based split only.
3. SQL model comparison by segment and store.
4. Inventory policy and simulation with three policies: `naive`, `forecast_no_ss`, `forecast_ss`.

## Results (2017 test year)

| Model | WMAPE | Bias |
|---|---|---|
| LightGBM | 4.41% | +0.35% |
| Seasonal naive | 6.22% | -3.67% |
| Naive | 6.48% | -0.08% |
| 4-week moving average | 7.49% | -0.16% |

LightGBM had the lowest WMAPE in every ABC class, XYZ class and store. Error was highest for C and Z series (5.64% and 5.65%).

| Policy | Stock-out days | Unmet units | Total cost (EUR) |
|---|---|---|---|
| naive | 2,292 | 66,475 | 649,006 |
| forecast_no_ss | 1,522 | 34,758 | 561,675 |
| forecast_ss | 189 | 3,224 | 492,429 |

- The forecast-based policy with safety stock cut total simulated cost by about 24% and stock-out days by about 92% versus naive, for about 4.7% more average inventory.
- About 13 points of the saving come from the better forecast and about 12 from safety stock.
- The ranking holds for any stock-out penalty above about 9% of lost margin (below that, naive is cheapest).

Charts are in `outputs/`.

## Limitations
- Costs, prices and lead times are assumed; savings are not real-world figures.
- Fill rate is already 99.4% for the naive policy, so the gain is in stock-out days and cost, not fill rate.
- z = 1.645 targets a cycle service level, not fill rate; the achieved fill rate (99.97%) is well above 95%, so z may be too high.
- Single-product (s, Q) logic only; no shared capacity, budgets or supplier constraints.
- ABC is less discriminating here because the 500 series have similar revenue.
- Daily demand is simulated from real sales; weekend effects were modest, so a flat weekly forecast / 7 is used as the daily rate.

## Future work
SARIMA/Prophet as extra models, quantile LightGBM for safety stock, lower service-level targets, PuLP budget constraint, Streamlit dashboard, real cost data, unit tests, PostgreSQL version.

## How to run
1. Install Python 3.11+ and MySQL 8+. 2. `python -m venv .venv`, activate it, `pip install -r requirements.txt`. 3. Copy `.env.example` to `.env` and set your password. 4. Put `train.csv` in `data/`. 5. `python -m src.db_setup`. 6. Run notebooks 01 to 08 in order.