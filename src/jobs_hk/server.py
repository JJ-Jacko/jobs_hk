from mcp.server.fastmcp import FastMCP

import jobs_hk.context as context
from jobs_hk.db import DB


mcp = FastMCP("Jobs HongKong")


if __name__ == "__main__":
    db = DB(context.engine)
    mcp.add_tool(db.get_jobs_basic_info)
    
    mcp.run(transport="stdio")
    