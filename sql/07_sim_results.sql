DROP TABLE IF EXISTS sim_results;

CREATE TABLE sim_results (
    store         TINYINT     NOT NULL,
    item          SMALLINT    NOT NULL,
    policy        VARCHAR(30) NOT NULL,
    service_level DOUBLE,
    stockouts     INT,
    avg_inventory DOUBLE,
    demand_units  DOUBLE,
    unmet_units   DOUBLE,
    holding_cost  DOUBLE,
    ordering_cost DOUBLE,
    stockout_cost DOUBLE,
    total_cost    DOUBLE,
    PRIMARY KEY (store, item, policy)
);