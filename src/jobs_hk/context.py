import os
from pathlib import Path

from dotenv import load_dotenv

from jobs_hk.other import load_config


__all__ = [
    # Path
    "DATA_BASE_FILE",
    
    # Path Container
    "PROMPTS",

    # Web
    "BASE_URLS",
    "USER_AGENT",

    # Config
    "CONFIG"
]


# Path
DATA_BASE_FILE = Path("data.db")
TOOLS_FILE = Path("tools.json")
CONFIG_FILE = Path("config.toml")

class PROMPTS:
    DIR = Path("prompts")
    
    SQL_GENERATOR = DIR / "sql_generator_sqlite_only.md"
    PROJECT_ASSISTANT = DIR / "project_assistant.md"

# Web
class BASE_URLS:
    JOB_GOV_HK = "https://www1.jobs.gov.hk"
    MOONSHOT = "https://api.moonshot.cn/v1"
    
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"

# Initialization
CONFIG = load_config(CONFIG_FILE)

load_dotenv()
MOONSHOT_API_KEY = os.environ.get("MOONSHOT_API_KEY", None)
