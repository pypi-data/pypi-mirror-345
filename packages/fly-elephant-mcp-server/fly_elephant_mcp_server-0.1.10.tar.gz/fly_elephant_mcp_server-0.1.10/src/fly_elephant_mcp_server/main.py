import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("fly_elephant_mcp_server")

@mcp.tool()
def getUseeUser()->str :
    """
    获取雅索当前用户信息
    """
    return "建平是总经理，春哥是副总经理"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
