# 节点：将结果持久化到数据库

from lg_agent.state import TripState

# 模拟持久化
def persist_result(state: TripState):
    
    print("正在将结果持久化到数据库...")

    # 模拟持久化时间
    import time
    time.sleep(3)

    # 后面用数据库工具函数持久化，这里先模拟结果
    print("持久化完成，保存的结果如下：")
    print({
        "intent_result": state["intent_result"],
        "query_results": state["query_results"],
        "user_feedback": state["user_feedback"]
    })
