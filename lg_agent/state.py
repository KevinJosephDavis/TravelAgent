# 定义 Graph State，承载所有业务数据
from typing import TypedDict, List, Optional, Dict
from langgraph.graph import MessagesState


# Optional表示字段可以为空，Optional[str] 等价于 Union[str,None]
# 需要注意：字段可以为空，但是必须得有这个 key

class UserPreferences(TypedDict):

    destination: Optional[str]
    budget: Optional[float]
    duration: Optional[int] # 旅游时长（单位：天）
    travel_companion: Optional[str]  # 家庭/情侣/独自
    travel_style: Optional[str]       # 休闲/特种兵/美食/拍照等
    dietary_restrictions: Optional[List[str]]  # 饮食禁忌
    mobility_restrictions: Optional[str]  # 行动不便情况
    past_preferences: Optional[List[str]]  # 历史偏好记录

class TripState(MessagesState):
    # 用户输入
    user_input: str
    user_preferences: UserPreferences

    # 业务中间结果
    intent_result: Optional[str]  # 意图分类结果
    route_planning: Optional[Dict]  # 生成的行程
    query_results: Optional[Dict]  # 天气/景点等查询结果
    booking_info: Optional[Dict]  # 预订信息
    budget_status: Optional[Dict]  # 预算状态
    emergency_info: Optional[Dict]  # 应急信息
    recommendations: Optional[List]  # 个性化推荐结果

    # 流程控制
    interrupt_needed: bool  # 是否需要人工确认
    user_feedback: Optional[str]  # 用户反馈/编辑内容
    is_complete: bool  # 流程是否结束
    current_step: Optional[str]  # 当前执行的节点，用于回退
    retry_count: int  # 工具调用重试计数，防止无限循环