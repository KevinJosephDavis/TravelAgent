# 天气查询

import requests
from typing import Optional

def get_weather_tool(city: str, date: Optional[str] = None) -> str:
    """
    查询指定城市实时天气的工具函数。
    :param city: 城市名称
    :param date: 日期（当前仅支持实时，若提供则返回提示）
    :return: 天气描述字符串
    """
    print("正在查询天气信息...")

    if not city:
        return "错误：未提供城市名称"

    # 清理城市名称字符串
    city_clean = city.strip().split("\n")[0].split(" ")[0]

    # 如果提供了日期，根据原逻辑返回提示
    if date and date.strip():
        return f"提示：当前工具仅支持查询实时天气，无法获取 {date} {city_clean} 的历史/未来天气数据。"

    try:
        # 使用 wttr.in API，如果不支持查询未来天气，后续可以再调整
        url = f"https://wttr.in/{city_clean}?format=j1"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # 解析数据
        weather_desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        temp_c = data["current_condition"][0]["temp_C"]
        
        result_str = f"{city_clean} 当前天气：{weather_desc}，温度：{temp_c}℃"
        
    except Exception as e:
        result_str = f"天气查询失败：{str(e)}"

    return result_str