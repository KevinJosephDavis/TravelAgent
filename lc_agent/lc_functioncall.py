import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from tavily import TavilyClient

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL  "),
    temperature=0,
)


class WeatherInput(BaseModel):
    city: str = Field(description="城市名称，例如：北京")
    date: str = Field(
        default="",
        description="查询日期（格式：YYYY-MM-DD）。当前工具仅支持实时天气，可留空。",
    )


class AttractionInput(BaseModel):
    city: str = Field(description="城市名称，例如：北京")
    weather: str = Field(description="天气情况，例如：晴天、阴天、Rainy")


@tool(args_schema=WeatherInput)
def get_weather(city: str, date: str = "") -> str:
    """查询指定城市实时天气。"""
    city = city.strip().split("\n")[0].split(" ")[0]
    if date and date.strip():
        return f"提示：当前工具仅支持查询实时天气，无法获取{date} {city}的天气数据。"
    try:
        url = f"https://wttr.in/{city}?format=j1"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        weather = data["current_condition"][0]["weatherDesc"][0]["value"]
        temp = data["current_condition"][0]["temp_C"]
        return f"{city} 当前天气：{weather}，温度：{temp}℃"
    except Exception as e:
        return f"天气查询失败：{str(e)}"


@tool(args_schema=AttractionInput)
def get_attraction(city: str, weather: str) -> str:
    """根据城市和天气推荐景点。"""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        query = f"{city} {weather} 适合去的景点推荐"
        resp = client.search(query=query, include_answer=True)
        answer = resp.get("answer", "未找到相关景点推荐")
        return str(answer).strip()
    except Exception as e:
        return f"景点推荐失败：{str(e)}"


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是旅游助手，用中文回答。"
            "你的任务是：先获取城市天气，再基于天气推荐景点。"
            "当用户说“上海呢”“那杭州呢”时，表示沿用上一轮同样任务但城市变更。"
            "严格规则：每次回答同一个城市时，get_weather 与 get_attraction 各最多调用一次；"
            "拿到有效景点结果后必须直接给最终回答，不要重复调用工具。",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output",
)

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt_template,
    tools=[get_weather, get_attraction],
)

agent_executor = AgentExecutor(
    agent=agent,
    memory=memory,
    tools=[get_weather, get_attraction],
    verbose=True,
    max_iterations=8,
    # generate:模型自己决定什么时候停 force:框架强制停止
    early_stopping_method="generate",
)