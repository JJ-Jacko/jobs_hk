from jobs_hk.libs.db import DB
from jobs_hk.libs.env import get_engine
from jobs_hk.libs.env import init_database


__all__ = [
    "db",
]


engine = get_engine()
init_database(engine)
db = DB(engine)
