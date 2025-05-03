from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp=FastMCP("fly_elephant_mcp_server")
EMP_PASSWORD=None

@mcp.tool()
def get_local_user_total()->Any:
    '''
    获取当前仓库内所有人员的数量
    :return:数量
    '''
    return "服务器异常,没有办法获取到人员的数量"

#外部传参解析并为全局变量赋值
def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='获取仓库用户信息')
    parser.add_argument("--password", type=str, required=True, help="用来连接的密码")
    args = parser.parse_args()
    global EMP_PASSWORD
    EMP_PASSWORD = args.password



def main():
    parse_args()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
