from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")


@mcp.tool()
def get_weather_info(name: str) -> str:
    """获取当前天气情况。
    Args：
        name: 城市
    """
    print("get_weather_info " + name)

    return "杭州天气晴朗。"
