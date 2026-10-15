-- Reusable view: forecast errors joined to segments
DROP VIEW IF EXISTS v_errors;

CREATE VIEW v_errors AS
SELECT f.model, f.store, f.item, f.week_start, f.actual, f.forecast,
       ABS(f.forecast - f.actual) AS abs_err,
       s.abc_class, s.xyz_class
FROM fact_forecast f
JOIN seg_abc_xyz s ON s.store = f.store AND s.item = f.item;