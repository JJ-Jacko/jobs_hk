import re


def match_re(pattern: str, src_str: str):
    m = re.search(pattern, src_str)
    
    if not m:
        return None
    
    return m.group(1)
