-- KPI views for the final report
DROP VIEW IF EXISTS v_kpi_policy;
CREATE VIEW v_kpi_policy AS
SELECT policy,
       ROUND(1 - SUM(unmet_units) / SUM(demand_units), 4) AS fill_rate,
       SUM(stockouts)                AS stockout_days,
       ROUND(SUM(avg_inventory))     AS avg_inventory_units,
       ROUND(SUM(holding_cost))      AS holding,
       ROUND(SUM(ordering_cost))     AS ordering,
       ROUND(SUM(stockout_cost))     AS stockout,
       ROUND(SUM(total_cost))        AS total
FROM sim_results
GROUP BY policy;

DROP VIEW IF EXISTS v_kpi_abc;
CREATE VIEW v_kpi_abc AS
SELECT s.abc_class, r.policy,
       ROUND(1 - SUM(r.unmet_units) / SUM(r.demand_units), 4) AS fill_rate,
       ROUND(SUM(r.total_cost)) AS total_cost
FROM sim_results r
JOIN seg_abc_xyz s ON s.store = r.store AND s.item = r.item
GROUP BY s.abc_class, r.policy;