from mcp.server.fastmcp import FastMCP

import jobs_hk.context as context
from jobs_hk.db import DB
from jobs_hk.services.assistant import Assistant


mcp = FastMCP("Jobs HongKong")


if __name__ == "__main__":
    db = DB(context.DATA_BASE_FILE)
    service = Assistant(
        host=context.CONFIG["ollama"]["host"],
        db=db
    )
    mcp.add_tool(db.get_jobs_basic_info)
    mcp.add_tool(service.query_jobs_database)
    
    mcp.run(transport="stdio")
    