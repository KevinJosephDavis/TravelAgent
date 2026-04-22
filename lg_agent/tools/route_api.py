# 路径规划API - 基于高德地图路径规划2.0

import requests
import os
from typing import Optional
from dotenv import load_dotenv
from lg_agent.utils.redis_client import redis_client, CACHE_EXPIRE_SECONDS
import json

load_dotenv()
AMAP_WEB_API_KEY = os.getenv("AMAP_WEB_API_KEY")

# 高德API地址
GEO_API_URL = "https://restapi.amap.com/v3/geocode/geo"
DRIVING_API_URL = "https://restapi.amap.com/v5/direction/driving"
WALKING_API_URL = "https://restapi.amap.com/v5/direction/walking"
BICYCLING_API_URL = "https://restapi.amap.com/v4/direction/bicycling"
TRANSIT_API_URL = "https://restapi.amap.com/v5/direction/transit/integrated"


def get_city_coordinates(city_name: str) -> Optional[str]:
    """
    将城市名转换为高德坐标（经度,纬度格式）
    :param city_name: 城市名称
    :return: 坐标字符串，如"116.397428,39.90923"
    """
    if not city_name:
        return None

    # 缓存Key
    cache_key = f"geo:{city_name}"

    # 先查缓存
    cached = redis_client.get(cache_key)
    if cached:
        print(f"缓存命中，直接返回{city_name}的坐标")
        return cached

    try:
        params = {
            "key": AMAP_WEB_API_KEY,
            "address": city_name,
            "output": "json"
        }
        resp = requests.get(GEO_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "1" and data.get("geocodes"):
            location = data["geocodes"][0].get("location")
            if location:
                # 缓存坐标（城市坐标相对稳定，缓存较长时间）
                redis_client.setex(cache_key, CACHE_EXPIRE_SECONDS * 24, location)
                return location

        print(f"未找到城市 {city_name} 的坐标")
        return None

    except Exception as e:
        print(f"地理编码失败：{str(e)}")
        return None


def get_route(origin: str, destination: str, travel_mode: str = "driving") -> dict:
    """
    获取两点之间的路径规划
    :param origin: 起点城市名
    :param destination: 终点城市名
    :param travel_mode: 出行方式（driving/walking/bicycling/transit）
    :return: 路径规划结果字典
    """
    print(f"正在规划从 {origin} 到 {destination} 的{travel_mode}路线...")

    # 参数校验
    if not origin or not destination:
        return {"error": "起点或终点为空"}

    # 构建缓存Key
    cache_key = f"route:{origin}:{destination}:{travel_mode}"

    # 先查缓存
    cached = redis_client.get(cache_key)
    if cached:
        print(f"缓存命中，直接返回从{origin}到{destination}的路线信息")
        try:
            return json.loads(cached)
        except:
            pass  # 如果解析失败，继续请求API

    # 获取起点和终点坐标
    origin_coord = get_city_coordinates(origin)
    dest_coord = get_city_coordinates(destination)

    if not origin_coord:
        return {"error": f"无法获取起点 {origin} 的坐标"}
    if not dest_coord:
        return {"error": f"无法获取终点 {destination} 的坐标"}

    # 根据出行方式调用不同API
    try:
        if travel_mode == "driving":
            result = _get_driving_route(origin_coord, dest_coord)
        elif travel_mode == "walking":
            result = _get_walking_route(origin_coord, dest_coord)
        elif travel_mode == "bicycling":
            result = _get_bicycling_route(origin_coord, dest_coord)
        elif travel_mode == "transit":
            result = _get_transit_route(origin_coord, dest_coord, origin)
        else:
            result = _get_driving_route(origin_coord, dest_coord)  # 默认驾车

        # 添加起点终点信息
        if "error" not in result:
            result["origin"] = origin
            result["destination"] = destination
            result["travel_mode"] = travel_mode

            # 缓存结果
            redis_client.setex(cache_key, CACHE_EXPIRE_SECONDS, json.dumps(result, ensure_ascii=False))

        return result

    except Exception as e:
        return {"error": f"路径规划失败：{str(e)}"}


def _get_driving_route(origin: str, destination: str) -> dict:
    """驾车路径规划"""
    params = {
        "key": AMAP_WEB_API_KEY,
        "origin": origin,
        "destination": destination,
        "extensions": "all",  # 返回全部信息
        "output": "json"
    }
    resp = requests.get(DRIVING_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "1":
        return {"error": f"驾车路径规划失败：{data.get('info')}"}

    return _parse_driving_result(data)


def _get_walking_route(origin: str, destination: str) -> dict:
    """步行路径规划"""
    params = {
        "key": AMAP_WEB_API_KEY,
        "origin": origin,
        "destination": destination,
        "output": "json"
    }
    resp = requests.get(WALKING_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "1":
        return {"error": f"步行路径规划失败：{data.get('info')}"}

    return _parse_walking_result(data)


def _get_bicycling_route(origin: str, destination: str) -> dict:
    """骑行路径规划"""
    params = {
        "key": AMAP_WEB_API_KEY,
        "origin": origin,
        "destination": destination,
        "output": "json"
    }
    resp = requests.get(BICYCLING_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "1":
        return {"error": f"骑行路径规划失败：{data.get('info')}"}

    return _parse_bicycling_result(data)


def _get_transit_route(origin: str, destination: str, city: str) -> dict:
    """公交路径规划（需要城市名）"""
    params = {
        "key": AMAP_WEB_API_KEY,
        "origin": origin,
        "destination": destination,
        "city": city,
        "output": "json"
    }
    resp = requests.get(TRANSIT_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "1":
        return {"error": f"公交路径规划失败：{data.get('info')}"}

    return _parse_transit_result(data)


def _parse_driving_result(data: dict) -> dict:
    """解析驾车路径规划结果"""
    route = data.get("route", {})
    paths = route.get("paths", [])

    if not paths:
        return {"error": "未找到可行路线"}

    # 取第一条路线
    path = paths[0]

    # 解析途径点/关键路段
    steps = []
    for step in path.get("steps", []):
        steps.append({
            "instruction": step.get("instruction"),
            "road": step.get("road"),
            "distance": step.get("distance"),
            "duration": step.get("duration")
        })

    return {
        "distance": path.get("distance"),  # 总距离（米）
        "duration": path.get("duration"),  # 总时间（秒）
        "tolls": path.get("tolls"),  # 过路费（元）
        "toll_distance": path.get("toll_distance"),  # 收费路段距离（米）
        "steps": steps[:10]  # 只返回前10个关键步骤，避免数据过多
    }


def _parse_walking_result(data: dict) -> dict:
    """解析步行路径规划结果"""
    route = data.get("route", {})
    paths = route.get("paths", [])

    if not paths:
        return {"error": "未找到可行路线"}

    path = paths[0]

    steps = []
    for step in path.get("steps", []):
        steps.append({
            "instruction": step.get("instruction"),
            "distance": step.get("distance"),
            "duration": step.get("duration")
        })

    return {
        "distance": path.get("distance"),
        "duration": path.get("duration"),
        "steps": steps[:10]
    }


def _parse_bicycling_result(data: dict) -> dict:
    """解析骑行路径规划结果"""
    data = data.get("data", {})
    paths = data.get("paths", [])

    if not paths:
        return {"error": "未找到可行路线"}

    path = paths[0]

    steps = []
    for step in path.get("steps", []):
        steps.append({
            "instruction": step.get("instruction"),
            "distance": step.get("distance"),
            "duration": step.get("duration")
        })

    return {
        "distance": path.get("distance"),
        "duration": path.get("duration"),
        "steps": steps[:10]
    }


def _parse_transit_result(data: dict) -> dict:
    """解析公交路径规划结果"""
    route = data.get("route", {})
    transits = route.get("transits", [])

    if not transits:
        return {"error": "未找到可行路线"}

    # 取前3个方案
    result_plans = []
    for transit in transits[:3]:
        segments = []
        for seg in transit.get("segments", []):
            seg_info = {
                "distance": seg.get("distance"),
                "duration": seg.get("duration")
            }
            # 公交/地铁信息
            if seg.get("bus"):
                bus_lines = seg["bus"].get("buslines", [])
                if bus_lines:
                    line = bus_lines[0]
                    seg_info["line_name"] = line.get("name")
                    seg_info["departure_stop"] = line.get("departure_stop", {}).get("name")
                    seg_info["arrival_stop"] = line.get("arrival_stop", {}).get("name")
            segments.append(seg_info)

        result_plans.append({
            "cost": transit.get("cost"),  # 费用
            "duration": transit.get("duration"),
            "walking_distance": transit.get("walking_distance"),
            "segments": segments
        })

    return {
        "plans": result_plans,
        "distance": route.get("distance"),
        "duration": transits[0].get("duration") if transits else 0
    }
