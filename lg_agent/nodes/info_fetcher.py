# 节点：实时信息查询（天气查询与预警、景点开放状态、交通状况、当地活动/节庆等）

from lg_agent.state import TripState
from lg_agent.tools.weather_api import get_weather_tool
from lg_agent.tools.extract_city import extract_city


def info_fetcher(state: TripState):
    
    print("正在查询实时信息...")

    user_input = state["user_input"]

    city = extract_city(user_input)

    # TODO : 这里由于wttr只能查询实时天气，所以先不传date，后续添加extract_date工具后再完善
    weather_info = get_weather_tool(city)

    return {
        "query_results": {"weather": weather_info}
    }