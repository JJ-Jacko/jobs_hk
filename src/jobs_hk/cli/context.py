from pathlib import Path

from jobs_hk.db import DB
from jobs_hk.env import get_engine
from jobs_hk.env import init_database
from jobs_hk.other import load_config


__all__ = [
    "project_config",
    "db",
]


# Path
project_config_p = Path("config.toml")

# Initialization
project_config = load_config(project_config_p)

engine = get_engine()
init_database(engine)
db = DB(engine)
