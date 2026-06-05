"""
最小可运行的 MCP Server：查询城市天气

依赖安装：  pip install "mcp[cli]"
本地调试：  mcp dev weather_server.py     （打开 Inspector，看 JSON-RPC 报文）
直接运行：  python weather_server.py       （stdio 传输，给 Claude Desktop 用）
"""

from mcp.server.fastmcp import FastMCP

# 这个对象就是整个 Server。
# "weather" 会出现在握手响应的 serverInfo.name 里。
# 变量名取 mcp，方便后面用 `mcp install` 一键注册到 Claude Desktop。
mcp = FastMCP("weather")


@mcp.tool()
def get_weather(city: str) -> str:
    """查询指定城市的当前天气。

    Args:
        city: 城市名，例如 "Melbourne"
    """
    # 真实场景这里会去调天气 API，例如：
    #   import httpx
    #   data = httpx.get(f"https://api.example.com/weather?city={city}").json()
    # 这里先用假数据，保证零依赖、开箱即跑。
    fake = {
        "Melbourne": "18°C，多云，东南风 15km/h",
        "Sydney": "23°C，晴",
        "Beijing": "9°C，霾",
    }
    result = fake.get(city, "暂无数据（试试 Melbourne / Sydney / Beijing）")
    return f"{city} 当前天气：{result}"


if __name__ == "__main__":
    # 不传参默认 stdio —— 正是 Claude Desktop 本地连接用的传输方式
    mcp.run()