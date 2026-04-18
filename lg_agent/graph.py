# 定义 LangGraph 状态、边，并编译整个图

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START


# 导入状态
from lg_agent.state import TripState

# 导入节点
from lg_agent.nodes.intent_router import intent_router
from lg_agent.nodes.info_fetcher import info_fetcher
from lg_agent.nodes.route_planning import route_planning
from lg_agent.nodes.interrupt_handler import interrupt_handler
from lg_agent.nodes.persist_result import persist_result

# 创建图
workflow = StateGraph(TripState)

# 添加节点
workflow.add_node("intent_router",intent_router) # 意图路由
workflow.add_node("info_fetcher",info_fetcher) # 信息查询
workflow.add_node("route_planning",route_planning) # 行程规划
workflow.add_node("interrupt_handler",interrupt_handler) # 用户确认/反馈
workflow.add_node("persist_result",persist_result) # 保存到数据库

# 添加边
workflow.add_edge(START,"intent_router")

# 意图路由：根据意图分类结果，路由到不同的节点
workflow.add_conditional_edges(
  "intent_router",
  lambda state: state["intent_result"], # 拿出 state 中的意图分类结果
  {
    "query_info": "info_fetcher",
    "plan_trip": "route_planning",
    "end": END
  } 
)

# 所有业务节点，都经过用户确认
workflow.add_edge("info_fetcher","interrupt_handler")
workflow.add_edge("route_planning","interrupt_handler")

# 用户确认、同意、保存结果
# 如果 state["is_complete"] 为 True（用户确认完成），则返回 accept，
# 否则（用户要修改）返回 edit
workflow.add_conditional_edges(
  "interrupt_handler",
  lambda state: "accept" if state["is_complete"] else "edit",
  {
    "accept": "persist_result",
    "edit": "intent_router" # 用户修改，回到意图路由重新执行
  }
)

# 保存结果，结束
workflow.add_edge("persist_result",END)

# 开启记忆
memory = MemorySaver()

# 编译
travel_agent = workflow.compile(checkpointer = memory)

# 流程图
# 开始
#   ↓
# 意图识别（查天气？还是规划行程？）
#   ↓
# → 查询天气/景点 → 给用户确认
# → 规划行程     → 给用户确认
#   ↓
# 用户确认
#   ↓
# → 同意 → 保存到数据库 → 结束
# → 修改 → 回到意图重新来


