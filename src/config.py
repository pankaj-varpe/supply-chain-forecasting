"""Single source of truth for paths, DB connection and ASSUMPTIONS.
Every assumed value here must be documented in the README."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")  # reads MYSQL_* from the .env file

DATA_DIR, SQL_DIR, OUT_DIR = ROOT / "data", ROOT / "sql", ROOT / "outputs"
CSV_PATH = DATA_DIR / "train.csv"

# --- Database connection (credentials come from .env, never hard-coded) ---
DB_NAME = os.getenv("MYSQL_DB", "supply_chain")
_url = dict(
    drivername="mysql+pymysql",
    username=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
)

def get_engine(with_db: bool = True):
    """Engine for the project DB (with_db=False connects to the server only)."""
    return create_engine(URL.create(**_url, database=DB_NAME if with_db else None))

SEED = 42

# --- ASSUMED cost parameters (dataset has none) ---
PRICE_RANGE = (1, 10)            # EUR
COST_RATIO_RANGE = (0.5, 0.7)    # unit cost as share of price
LEAD_TIME_RANGE = (3, 14)        # days, inclusive
HOLDING_COST_RATE = 0.20         # per year
ORDER_COST_RANGE = (20, 50)      # EUR per order
REGIONS = ["North", "South", "East", "West"]

# --- Analysis settings (ASSUMED, review after seeing the data) ---
FIRST_WEEK = "2013-01-07"        # first full Monday-Sunday week
TRAIN_END = "2017-01-01"         # a Sunday: 208 full training weeks
TEST_START = "2017-01-02"        # a Monday: 52 full test weeks
VAL_START = "2016-01-04"         # first Monday of 2016: hold-out year for estimating error sigma
SIM_START, SIM_END = "2017-01-02", "2017-12-31"
SERVICE_LEVEL = 0.95
ABC_THRESHOLDS = (0.80, 0.95)    # cumulative revenue share
STOCKOUT_PENALTY_MULT = 1.0      # stock-out cost = lost margin x this (ASSUMED, test sensitivity)