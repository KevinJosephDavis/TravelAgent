# 天气查询

import requests
from typing import Optional
from lg_agent.utils.redis_client import redis_client, CACHE_EXPIRE_SECONDS

API_URL = "https://wttr.in/{city}?format=j1"  

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
    

    # 构建缓存 Key
    cache_key = f"weather:{city_clean}"

    try:

        # import time
        # # 统计 get 的时间
        # start_time = time.time() * 1000

        # 先查缓存
        cache_weather_data = redis_client.get(cache_key)

        # end_time = time.time() * 1000
        # print(f"Redis GET 用时：{end_time - start_time:.2f}毫秒")

        # 如果缓存命中，直接返回
        if cache_weather_data:
            print(f"缓存命中，直接返回{city_clean}的天气信息")
            return cache_weather_data # decode_responses=True 已经设置了自动解码，这里直接返回字符串即可
        
        # 如果缓存未命中，则从API获取数据
        # 使用 wttr.in API，如果不支持查询未来天气，后续可以再调整
        url = API_URL.format(city=city_clean)
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # 解析数据
        weather_desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        temp_c = data["current_condition"][0]["temp_C"]
        
        result_str = f"{city_clean} 当前天气：{weather_desc}，温度：{temp_c}℃"

        # 将结果缓存到 Redis，设置过期时间
        redis_client.setex(cache_key, CACHE_EXPIRE_SECONDS, result_str)

    except Exception as e:
        result_str = f"天气查询失败：{str(e)}"

    return result_str