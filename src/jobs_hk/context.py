from pathlib import Path

from jobs_hk.other import load_config


__all__ = [
    # Path
    "DATA_BASE_FILE",
    "SQL_GENERATOR_SQLITE_ONLY_FILE",
    "ASSISTANT_FILE",

    # Config
    "CONFIG"
]


# Path
PROMPTS_DIR = Path("prompts")

DATA_BASE_FILE = Path("data.db")
CONFIG_FILE = Path("config.toml")
SQL_GENERATOR_SQLITE_ONLY_FILE = PROMPTS_DIR / "sql_generator_sqlite_only.md"
ASSISTANT_FILE = PROMPTS_DIR / "project_assistant.md"

# Initialization
CONFIG = load_config(CONFIG_FILE)
