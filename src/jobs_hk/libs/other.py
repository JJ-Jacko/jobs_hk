import re
from typing import Dict

from jobs_hk.types import UNSET


def get_fields_setted(payload: Dict[str, any]):
    return {
        k: v
        for k, v in payload.items()
        if v is not UNSET
    }


def match_re(pattern: str, src_str: str):
    m = re.search(pattern, src_str)
    
    if not m:
        return None
    
    return m.group(1)


def fill_none(content: str):
    if content in ["-"]:
        return None
    else:
        content
