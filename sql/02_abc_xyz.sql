-- ABC / XYZ segmentation per store-item, using TRAINING weeks only.
-- Parameters (filled in from config.py) start with a colon.
DROP TABLE IF EXISTS seg_abc_xyz;

CREATE TABLE seg_abc_xyz AS
WITH revenue AS (
    -- ABC input: revenue = units x assumed unit price
    SELECT s.store, s.item, SUM(s.units * i.unit_price) AS revenue
    FROM sales s
    JOIN dim_item i ON i.item = s.item
    WHERE s.date BETWEEN :first_week AND :train_end
    GROUP BY s.store, s.item
),
abc AS (
    -- Window functions: running revenue total divided by grand total
    SELECT store, item, revenue,
           SUM(revenue) OVER (ORDER BY revenue DESC, store, item)
             / SUM(revenue) OVER () AS cum_share
    FROM revenue
),
weekly AS (
    -- Monday of each week, then total units per store-item-week
    SELECT store, item,
           DATE_SUB(date, INTERVAL WEEKDAY(date) DAY) AS week_start,
           SUM(units) AS units
    FROM sales
    WHERE date BETWEEN :first_week AND :train_end
    GROUP BY store, item, week_start
),
xyz AS (
    -- Coefficient of variation of weekly demand, plus its tertile (1 = lowest third)
    SELECT store, item,
           AVG(units) AS mean_weekly,
           STDDEV_SAMP(units) / AVG(units) AS cv,
           NTILE(3) OVER (ORDER BY STDDEV_SAMP(units) / AVG(units)) AS tile
    FROM weekly
    GROUP BY store, item
)
SELECT a.store, a.item, a.revenue, a.cum_share,
       CASE WHEN a.cum_share <= :a_cut THEN 'A'
            WHEN a.cum_share <= :b_cut THEN 'B'
            ELSE 'C' END AS abc_class,
       x.mean_weekly, x.cv,
        CASE x.tile WHEN 1 THEN 'X'
                    WHEN 2 THEN 'Y'
                   ELSE 'Z' END AS xyz_class
FROM abc a
JOIN xyz x USING (store, item);