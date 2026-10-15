-- Weekly feature table per store-item.
-- Every lag and rolling feature looks only at EARLIER weeks (no leakage).
DROP TABLE IF EXISTS features_weekly;

CREATE TABLE features_weekly AS
WITH weekly AS (
    -- Monday of each week, then total units per store-item-week
    SELECT store, item,
           DATE_SUB(date, INTERVAL WEEKDAY(date) DAY) AS week_start,
           CAST(SUM(units) AS SIGNED) AS units
    FROM sales
    WHERE date BETWEEN :first_week AND :sim_end
    GROUP BY store, item, week_start
)
SELECT store, item, week_start, units,
       LAG(units, 1)  OVER w AS lag_1,
       LAG(units, 2)  OVER w AS lag_2,
       LAG(units, 4)  OVER w AS lag_4,
       LAG(units, 52) OVER w AS lag_52,
       -- Rolling means end at the PREVIOUS week, never include the current one
       CAST(AVG(units) OVER (w ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING) AS DOUBLE)  AS roll4_mean,
       CAST(AVG(units) OVER (w ROWS BETWEEN 13 PRECEDING AND 1 PRECEDING) AS DOUBLE) AS roll13_mean,
       WEEKOFYEAR(week_start) AS week_of_year,
       MONTH(week_start) AS month_num,
       CASE WHEN week_start <= :train_end THEN 'train' ELSE 'test' END AS data_split
FROM weekly
WINDOW w AS (PARTITION BY store, item ORDER BY week_start);