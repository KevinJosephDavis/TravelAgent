# 节点：实时信息查询（天气查询与预警、景点开放状态、交通状况、当地活动/节庆等）

from lg_agent.state import TripState
from lg_agent.tools.weather_api import get_weather_tool
from lg_agent.tools.extract_city import extract_city
from lg_agent.tools.traffic_api import get_city_traffic_event
from lg_agent.tools.spot_api import get_attraction_recommendation

# TODO : 后续让 LLM 判断用户具体要查什么信息，天气？交通？景点？活动？目前先全部返回
def info_fetcher(state: TripState):
    
    print("正在查询实时天气与交通信息，并为您推荐景点...")

    user_input = state["user_input"]

    city = extract_city(user_input)

    # TODO : 这里由于wttr只能查询实时天气，所以先不传date，后续添加extract_date工具后再完善

    # 统计查询用时
    import time

    start_time = time.time() * 1000

    weather_info = get_weather_tool(city)

    end_time = time.time() * 1000
    
    print(f"天气查询用时：{end_time - start_time:.2f}毫秒")

    # traffic_info = get_city_traffic_event(city)

    # 这里要对 traffic_info 进行处理，因为它是一个字典，而传进去的参数是字符串
    # 而且，应该尽可能让传进去的信息简洁，因此要将 traffic_info 中的 brief 提取出来合并为一个字符串

    # traffic_info_brief = ", ".join([event["brief"] for event in traffic_info])

    # TODO :这里由于高德的 API 是商用的，需要等待一段时间处理，因此先把交通信息写死，后续再恢复

    traffic_info_brief = "交通状况：道路畅通，无重大事故或施工。"

    # 统计查询用时
    start_time = time.time() * 1000
    
    attraction_info = get_attraction_recommendation(city, weather_info, traffic_info_brief)

    end_time = time.time() * 1000
    print(f"景点推荐用时：{end_time - start_time:.2f}毫秒")

    return { 
        "query_results": {
            "weather": weather_info,
            "traffic": traffic_info_brief,
            "attraction": attraction_info
        }
    }