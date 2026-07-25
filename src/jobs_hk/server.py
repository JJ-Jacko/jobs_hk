from typing import Any
from typing import Dict
from typing import List

from mcp.server.fastmcp import FastMCP

import jobs_hk.context as context
from jobs_hk.db import DB


mcp = FastMCP("Jobs HongKong")
db = DB(context.engine)


@mcp.tool()
def get_jobs_basic_info(num: int = 5) -> List[Dict[str, Any]]:
    """
    Get the Hongkong jobs basic information in the project database.
    
    Args:
        num: The number of the jobs basic info of Hongkong Jobs database.
    
    """
    
    info = db.get_jobs_basic_info(num)
    
    return info


if __name__ == "__main__":
    mcp.run(transport="stdio")
    