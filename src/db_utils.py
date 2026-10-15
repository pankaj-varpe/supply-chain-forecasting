"""Small helper: run a .sql file from the sql/ folder against MySQL."""
from sqlalchemy import text

from src import config as C


def run_sql_file(filename, params=None):
    sql = (C.SQL_DIR / filename).read_text()
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    with C.get_engine().begin() as con:
        for s in statements:
            # pass only the parameters this statement actually uses
            used = {k: v for k, v in (params or {}).items() if f":{k}" in s}
            con.execute(text(s), used)