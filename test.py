# test.py
from lg_agent.graph import travel_agent

def test_graph():
    import uuid
    memory_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": memory_id}}

    inputs = {
        "user_input": "番禺区的天气与交通情况怎么样",
        "user_preferences": {},
        "interrupt_needed": True,
        "is_complete": True,
        "retry_count": 0
    }

    print("开始运行 LangGraph 旅游助手...")
    result = travel_agent.invoke(inputs, config=config)
    print("✅ 运行成功！")
    print(result)

if __name__ == "__main__":
    test_graph()