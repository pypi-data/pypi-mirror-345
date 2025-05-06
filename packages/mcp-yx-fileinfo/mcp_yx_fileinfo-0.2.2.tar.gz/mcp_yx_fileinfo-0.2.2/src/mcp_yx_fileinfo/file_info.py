from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP server
mcp = FastMCP("weather")

# Constants
AMAP_API_KEY = "f3cab8d805d2e46a5e96268a84393b4b"  # 请替换为您的高德地图API密钥
AMAP_WEATHER_API = "https://restapi.amap.com/v3/weather/weatherInfo"


async def make_amap_request(url: str, params: dict) -> dict[str, Any] | None:
    """向高德地图 API 发送请求，并进行适当的错误处理。"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"请求错误: {e}")
            return None


def format_weather(weather_data: dict) -> str:
    """将天气数据格式化为可读的字符串。"""
    lives = weather_data.get("lives", [{}])[0]
    return f"""
城市: {lives.get('city', '未知')}
天气: {lives.get('weather', '未知')}
温度: {lives.get('temperature', '未知')}°C
风向: {lives.get('winddirection', '未知')}
风力: {lives.get('windpower', '未知')}级
湿度: {lives.get('humidity', '未知')}%
时间: {lives.get('reporttime', '未知')}
"""


@mcp.tool()
async def get_weather(city: str) -> str:
    """获取中国城市的实时天气。

    Args:
        city: 城市名称（例如：北京、上海、广州）
    """
    params = {
        "key": AMAP_API_KEY,
        "city": city,
        "extensions": "base"
    }

    data = await make_amap_request(AMAP_WEATHER_API, params)

    if not data:
        return "无法获取天气数据。"

    if data.get("status") != "1":
        return f"获取天气数据失败: {data.get('info', '未知错误')}"

    if not data.get("lives"):
        return "未找到该城市的天气数据。"

    return format_weather(data)





