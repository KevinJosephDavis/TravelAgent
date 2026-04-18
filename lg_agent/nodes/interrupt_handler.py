# 节点：人工确认/用户反馈处理

from lg_agent.state import TripState

# 模拟用户确认/反馈处理
# LangGraph 节点只能通过 return 修改状态，不能直接赋值修改状态
def interrupt_handler(state: TripState):
    print("正在处理用户确认/反馈...")

    confirm = input("请确认是否完成当前步骤（y/n）：")
    if confirm.lower() == "y":
        print("用户确认完成，继续执行后续步骤...")
        return {
            "is_complete": True,
            "user_feedback": "用户确认完成"
        }
    else:
        print("用户取消，停止执行后续步骤...")
        return {
            "is_complete": False,
            "user_feedback": "用户取消"
        } 