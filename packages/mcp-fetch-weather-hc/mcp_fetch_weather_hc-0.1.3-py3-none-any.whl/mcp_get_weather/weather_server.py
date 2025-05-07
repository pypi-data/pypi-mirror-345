import json
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")

# Seniverse API 配置
SENIVERSE_API_BASE = "https://api.seniverse.com/v3/weather/now.json"
API_KEY = "ST5th6y1Nf0Au_Ypr"  # 你的 Seniverse API Key
USER_AGENT = "weather-app/1.0"

async def fetch_weather_seniverse(city: str) -> dict[str, Any] | None:
    """
    从 Seniverse API 获取天气信息
    :param city: 城市名称
    :return: 天气数据字典；若出错返回包含 error 信息的字典
    """
    params = {
        "key": API_KEY,
        "location": city,
        "language": "zh-Hans",
        "unit": "c"
    }
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(SENIVERSE_API_BASE, params=params,
                                       headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP 错误: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

def format_weather_seniverse(data: dict[str, Any] | str) -> str:
    """
    将 Seniverse 天气数据格式化为易读文本。
    :param data: 天气数据（可以是字典或 JSON 字符串）
    :return: 格式化后的天气信息字符串
    """
    # 如果传入的是字符串，则先转换为字典
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f"无法解析天气数据: {e}"
    # 如果数据中包含错误信息，直接返回错误提示
    if "error" in data:
        return f"⚠️ {data['error']}"
    # 提取数据时做容错处理
    results = data.get("results", [])
    if not results:
        return "⚠️ 未找到天气信息"
    now = results[0].get("now", {})
    city = results[0].get("location", {}).get("name", "未知")
    temperature = now.get("temperature", "N/A")
    description = now.get("text", "未知")
    return (
        f"📍 城市: {city}\n"
        f"🌡 温度: {temperature}°C\n"
        f"🌤 天气: {description}\n"
    )

@mcp.tool()
async def query_weather_seniverse(city: str) -> str:
    """
    输入指定城市的中文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用中文，如 厦门）
    :return: 格式化后的天气信息
    """
    data = await fetch_weather_seniverse(city)
    return format_weather_seniverse(data)



def main():
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='sse')

if __name__ == "__main__":

    main()