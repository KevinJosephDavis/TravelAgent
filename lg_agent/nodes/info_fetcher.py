# 节点：实时信息查询（天气查询与预警、景点开放状态、交通状况、当地活动/节庆等）


from lg_agent.state import TripState

def info_fetcher(state: TripState):
    
    print("正在查询实时信息...")

    # 模拟查询时间
    import time
    time.sleep(3)

    # 后面用工具函数查询实时信息，这里先模拟结果
    return {
        "query_results": {
            "weather": "晴，25度",
            "traffic": "畅通",
            "events": ["音乐节", "美食节"]
        }
    }