from pathlib import Path

from jobs_hk.db import DB
from jobs_hk.env import get_engine
from jobs_hk.env import init_database
from jobs_hk.other import load_config


__all__ = [
    # Path
    "f_sql_generator_sqlite_only",
    "f_project_assistant",

    # Config
    "project_config",

    # Other
    "db"
]


# Path
d_prompts = Path("prompts")

f_project_config = Path("config.toml")
f_sql_generator_sqlite_only = d_prompts / "sql_generator_sqlite_only.md"
f_project_assistant = d_prompts / "project_assistant.md"

# Initialization
project_config = load_config(f_project_config)

engine = get_engine()
init_database(engine)
db = DB(engine)
