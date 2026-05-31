from jobs_hk.db import DB
from jobs_hk.env import get_engine
from jobs_hk.env import init_database


__all__ = [
    "db",
]


engine = get_engine()
init_database(engine)
db = DB(engine)
