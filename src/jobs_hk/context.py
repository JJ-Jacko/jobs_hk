from pathlib import Path

from jobs_hk.other import load_config


__all__ = [
    # Path
    "DATA_BASE_FILE",
    
    # Path Container
    "PROMPTS",

    # Config
    "CONFIG"
]


# Path
DATA_BASE_FILE = Path("data.db")
CONFIG_FILE = Path("config.toml")

class PROMPTS:
    DIR = Path("prompts")
    
    SQL_GENERATOR = DIR / "sql_generator_sqlite_only.md"
    PROJECT_ASSISTANT = DIR / "project_assistant.md"


# Initialization
CONFIG = load_config(CONFIG_FILE)
