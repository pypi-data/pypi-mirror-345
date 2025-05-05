
from mcp.server.fastmcp import FastMCP
import datetime
mcp = FastMCP()
 
@mcp.tool()
def get_time() -> str:
    """获取当前系统时间"""
    return str(datetime.datetime.now()+"有点东西")
 
if __name__ == "__main__":
    mcp.run(transport='stdio')
