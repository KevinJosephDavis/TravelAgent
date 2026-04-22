# 从用户输入中提取路径规划所需信息：起点、终点、出行方式

from lg_agent.tools.init_llm import init_llm
from lg_agent.prompts.prompt import EXTRACT_ROUTE_PROMPT


def extract_city_route(user_input: str) -> dict:
    """
    从用户输入里抽取出路径规划所需的信息
    :param user_input: 用户输入的字符串
    :return: 包含origin（起点）、destination（终点）、travel_mode（出行方式）的字典
    """

    # TODO: 后续接入LLM进行真正的信息抽取
    # prompt = EXTRACT_ROUTE_PROMPT.format(user_input=user_input)
    # llm = init_llm()
    # response = llm.invoke(prompt)
    # content = response.content.strip()

    # 暂时写死返回结果用于测试
    return {
        "origin": "广州",
        "destination": "深圳",
        "travel_mode": "driving"
    }


def normalize_travel_mode(mode: str) -> str:
    """
    标准化出行方式为API支持的类型
    :param mode: 用户输入的出行方式
    :return: 标准化的出行方式（driving/walking/bicycling/transit）
    """
    mode_lower = mode.lower()

    # 驾车相关
    if any(kw in mode_lower for kw in ["驾", "开车", "自驾", "汽车", "driving", "car"]):
        return "driving"

    # 步行相关
    if any(kw in mode_lower for kw in ["步", "走", "走路", "步行", "walking", "walk"]):
        return "walking"

    # 骑行相关
    if any(kw in mode_lower for kw in ["骑", "骑行", "自行车", "单车", "bicycling", "bike", "cycling"]):
        return "bicycling"

    # 公交相关
    if any(kw in mode_lower for kw in ["公交", "地铁", "公共交通", "transit", "bus", "subway", "metro"]):
        return "transit"

    # 默认驾车
    return "driving"
