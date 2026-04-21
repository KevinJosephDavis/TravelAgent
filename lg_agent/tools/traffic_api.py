import requests
import time
import hashlib
import os
from dotenv import load_dotenv
from lg_agent.constants.city_code import CITY_ADCODE_MAP


load_dotenv()
AMAP_WEB_API_KEY = os.getenv("AMAP_WEB_API_KEY")
AMAP_WEB_API_URL = "https://et-api.amap.com/event/queryByAdcode"


def generate_digest(client_key: str, timestamp: str) -> str:
    """高德官方要求：动态鉴权签名 digest = sha1(key+timestamp) 小写十六进制"""
    raw_str = client_key + timestamp
    sha1_obj = hashlib.sha1(raw_str.encode("utf-8"))
    return sha1_obj.hexdigest().lower()

def get_city_traffic_event(city_name: str):
    """
    根据城市名查询实时交通事件（事故/施工/管制）
    :param city_name: 提取出的城市名，如北京
    :return: 结构化交通信息
    """
    # 1. 城市名转adcode
    adcode = CITY_ADCODE_MAP.get(city_name)
    if not adcode:
        return {"error": f"暂不支持该城市：{city_name}"}
    
    # 2. 生成秒级时间戳
    timestamp = str(int(time.time()))
    
    # 3. 生成高德动态鉴权digest
    digest = generate_digest(AMAP_WEB_API_KEY, timestamp)
    
    # 4. 组装请求参数（全部必填项）
    params = {
        "adcode": adcode,
        "clientKey": AMAP_WEB_API_KEY,
        "timestamp": timestamp,
        "digest": digest,
        "eventType": "1;2;3",  # 1事故 2施工 3管制，分号分隔查全部
        "isExpressway": 0     # 0=市区全部道路，1=仅高速
    }

    try:
        resp = requests.get(AMAP_WEB_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        return parse_traffic_result(result)
    except Exception as e:
        return {"error": f"交通接口请求失败：{str(e)}"}

def parse_traffic_result(raw_data):
    """解析高德返回的原始JSON，整理成前端友好的简洁格式"""
    if raw_data.get("code") != 0:
        return {"error": f"接口调用失败：{raw_data.get('msg')}"}
    
    event_list = raw_data.get("data", [])
    traffic_info = []
    for item in event_list:
        traffic_info.append({
            "事件类型": item.get("eventType"),
            "标题": item.get("brief"),
            "详情描述": item.get("eventDesc"),
            "涉及道路": item.get("roadName"),
            "开始时间": item.get("startTime"),
            "结束时间": item.get("endTime"),
            "是否高速": item.get("expressway")
        })
    
    return {
        "城市": raw_data.get("adcode"),
        "事件总数": len(traffic_info),
        "实时交通事件": traffic_info
    }