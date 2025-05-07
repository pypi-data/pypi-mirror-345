from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pokemon")

@mcp.tool(description="获取本地天气")
def get_pokemon_info(name: str) -> str:
    """
   获取本地天气信息
    Args:
        name: 城市名称
    """

    if name == "杭州":
        return "晴空万里"
    if name == "上海":
        return "多云转晴"
    if name == "西北":
        return "冰封千里"
    return "母鸡了"
