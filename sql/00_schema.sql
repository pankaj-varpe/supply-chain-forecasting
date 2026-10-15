-- Raw data and assumed dimensions are rebuilt on every run.
-- Output tables (fact_forecast, sim_results) are kept between runs.
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS dim_item;
DROP TABLE IF EXISTS dim_store;

CREATE TABLE sales (
    date  DATE     NOT NULL,
    store TINYINT  NOT NULL,
    item  SMALLINT NOT NULL,
    units INT      NOT NULL,
    PRIMARY KEY (store, item, date)   -- also rejects duplicate rows
);

CREATE TABLE dim_item (               -- ASSUMED values
    item              SMALLINT PRIMARY KEY,
    unit_price        DECIMAL(6,2),
    unit_cost         DECIMAL(6,2),
    lead_time_days    TINYINT,
    holding_cost_rate DECIMAL(4,2),
    order_cost        DECIMAL(6,2)
);

CREATE TABLE dim_store (              -- ASSUMED values
    store  TINYINT PRIMARY KEY,
    region VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS fact_forecast (
    store      TINYINT     NOT NULL,
    item       SMALLINT    NOT NULL,
    week_start DATE        NOT NULL,
    model      VARCHAR(30) NOT NULL,
    actual     DOUBLE,
    forecast   DOUBLE,
    PRIMARY KEY (store, item, week_start, model)
);
