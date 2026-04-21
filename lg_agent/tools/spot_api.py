# 使用 Tavily 进行景点推荐
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# 根据城市、当地天气与当地交通情况推荐景点
# TODO : 后续可以添加用户偏好参数，如喜欢自然风光、历史人文、还是现代娱乐等，以提供更个性化的推荐
# TODO : 可能需要考虑将 Tavily 返回的结果翻译为中文，以及对 Tavily 返回的结果通过 LLM 进行结构化，现在暂时写死“用中文返回”
def get_attraction_recommendation(city: str, weather: str, traffic: str) -> str:
    """根据城市、当地天气与当地交通情况推荐景点"""

    print("正在查询景点推荐...")

    # 构建缓存 Key
    cache_key = f"spot_recommendation:{city}"

    try:
        # 先查缓存
        from lg_agent.utils.redis_client import redis_client, CACHE_EXPIRE_SECONDS
        cache_spot_data = redis_client.get(cache_key)
        if cache_spot_data:
            print(f"缓存命中，直接返回{city}的景点推荐")
            return cache_spot_data

        query = f"{city} {weather} {traffic} 适合去的景点推荐，用中文返回结果"

        resp = tavily_client.search(
            query=query, 
            include_answer="basic",
            search_depth="advanced"
        )
        answer = resp.get("answer", "未找到相关景点推荐")
        result = "推荐景点：" + str(answer).strip()

        # 缓存结果，转为字符串存储
        redis_client.setex(cache_key, CACHE_EXPIRE_SECONDS, str(result))
        return result
    except Exception as e:
        return f"景点推荐失败：{str(e)}"
