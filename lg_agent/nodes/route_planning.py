# 节点：路径规划（起点到终点的路线查询）
from lg_agent.state import TripState
from lg_agent.tools.extract_city_route import extract_city_route
from lg_agent.tools.route_api import get_route


def route_planning(state: TripState) -> dict:
    """
    路径规划节点：从用户输入中提取起点终点，调用高德API获取路线规划
    :param state: 当前状态
    :return: 更新后的状态字典
    """
    print("正在规划行程...")

    # 从state中获取用户输入
    user_input = state.get("user_input", "")

    if not user_input:
        return {
            "route_planning": {"error": "用户输入为空"}
        }

    # 提取起点、终点和出行方式
    # TODO : 如果用户是要去某地，要先拿到用户所在的位置，作为起点
    route_info = extract_city_route(user_input)
    origin = route_info.get("origin", "")
    destination = route_info.get("destination", "")
    travel_mode = route_info.get("travel_mode", "driving")

    print(f"提取信息 - 起点: {origin}, 终点: {destination}, 出行方式: {travel_mode}")

    # 校验提取结果
    if not origin or not destination:
        return {
            "route_planning": {
                "error": "无法识别起点或终点，请提供明确的出发地和目的地",
                "extracted_info": route_info
            }
        }

    # 调用路径规划API
    route_result = get_route(origin, destination, travel_mode)

    # 返回结果
    return {
        "route_planning": route_result
    }
