# 节点：意图分类

# 先空实现，跑通了再调用LLM


from lg_agent.state import TripState

def intent_router(state: TripState):
    
    print("正在识别用户意图...")

    import time
    time.sleep(3)  # 模拟处理时间

    # 后面用LLM判断意图
    return {
        "intent_result": "query_info"  # 先默认查询信息
    }