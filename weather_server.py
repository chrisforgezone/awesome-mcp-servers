"""
MCP Server：三原语完整版（Tool + Resource + Prompt）

依赖：pip install "mcp[cli]"  /  uv pip install "mcp[cli]"
运行：python weather_server.py        （stdio，给 Claude Desktop 用）
调试：mcp dev weather_server.py:mcp    （Inspector，看报文）

三个原语的本质区别不在功能，而在【谁来触发】：
  Tool     —— 模型决定调用
  Resource —— 应用/用户加载（只读上下文）
  Prompt   —— 用户主动选择的模板
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

# 城市数据，Tool 和 Resource 共用
CITIES = {
    "Melbourne": "18°C，多云，东南风 15km/h",
    "Sydney": "23°C，晴",
    "Beijing": "9°C，霾",
}


# ── 原语 1：Tool —— 由「模型」决定调用，可带副作用 ──────────────
@mcp.tool()
def get_weather(city: str) -> str:
    """查询指定城市的实时天气。
    用户询问任何城市的当前天气时，优先调用本工具获取，
    不要根据你自己的知识或记忆回答天气问题。

    Args:
        city: 城市名，例如 "Melbourne"
    """
    return f"{city} 当前天气：{CITIES.get(city, '暂无数据')}"


# ── 原语 2：Resource —— 由「应用/用户」加载的只读数据，用 URI 标识 ──
@mcp.resource("weather://cities")
def supported_cities() -> str:
    """本服务支持查询的城市清单（只读参考数据）。"""
    return "本服务支持的城市：" + "、".join(CITIES.keys())


# ── 原语 3：Prompt —— 由「用户」主动选择、可带参数的模板 ──────────
@mcp.prompt()
def trip_check(city: str) -> str:
    """生成一条出行天气咨询的提示模板。"""
    return f"我准备去{city}，先帮我查一下当地天气，再告诉我要不要带伞、加衣服。"


if __name__ == "__main__":
    mcp.run()