"""Create the MySQL database, load train.csv, fill ASSUMED dimension tables.
Run from the project root:  python -m src.db_setup"""
import numpy as np
import pandas as pd
from sqlalchemy import text

from src import config as C


def build_db():
    # 1. Create the database if it does not exist (server-level connection)
    with C.get_engine(with_db=False).begin() as con:
        con.execute(text(f"CREATE DATABASE IF NOT EXISTS `{C.DB_NAME}`"))

    engine = C.get_engine()

    # 2. Create tables from the schema file (split into single statements)
    schema = (C.SQL_DIR / "00_schema.sql").read_text()
    statements = [s.strip() for s in schema.split(";") if s.strip()]
    with engine.begin() as con:
        for s in statements:
            con.execute(text(s))

    # 3. Load raw sales. Parsing the date here catches bad date formats early.
    df = pd.read_csv(C.CSV_PATH, parse_dates=["date"]).rename(columns={"sales": "units"})
    print(f"Loading {len(df):,} rows into MySQL (1-3 minutes)...")
    df.to_sql("sales", engine, if_exists="append", index=False,
              chunksize=20000, method="multi")

    # 4. Assumed dimension tables, fixed seed -> anyone gets identical values
    rng = np.random.default_rng(C.SEED)
    items = np.sort(df["item"].unique())
    price = rng.uniform(*C.PRICE_RANGE, len(items)).round(2)
    pd.DataFrame({
        "item": items,
        "unit_price": price,
        "unit_cost": (price * rng.uniform(*C.COST_RATIO_RANGE, len(items))).round(2),
        "lead_time_days": rng.integers(C.LEAD_TIME_RANGE[0], C.LEAD_TIME_RANGE[1] + 1, len(items)),
        "holding_cost_rate": C.HOLDING_COST_RATE,
        "order_cost": rng.uniform(*C.ORDER_COST_RANGE, len(items)).round(2),
    }).to_sql("dim_item", engine, if_exists="append", index=False)

    stores = np.sort(df["store"].unique())
    pd.DataFrame({"store": stores, "region": rng.choice(C.REGIONS, len(stores))}
                 ).to_sql("dim_store", engine, if_exists="append", index=False)

    # 5. Sanity checks
    def q(sql):
        return pd.read_sql(text(sql), engine)
    print("\nrows:", q("SELECT COUNT(*) AS n FROM sales").iloc[0, 0])
    print(q("SELECT MIN(date) AS first_day, MAX(date) AS last_day, "
            "COUNT(DISTINCT store) AS stores, COUNT(DISTINCT item) AS items FROM sales"))
    print("negative units:", q("SELECT COUNT(*) FROM sales WHERE units < 0").iloc[0, 0])
    print(q("SELECT * FROM dim_item LIMIT 5"))


if __name__ == "__main__":
    build_db()