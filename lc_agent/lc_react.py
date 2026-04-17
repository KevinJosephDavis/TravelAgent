import json
import os
from json import JSONDecoder

import requests
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0
)


def _json_objects_in_text(s: str) -> list[dict]:
    """从可能含杂质的字符串中依次抠出 JSON 对象（ReAct 常把 Observation 粘在 Action Input 后面）。"""
    dec = JSONDecoder()
    out: list[dict] = []
    i = 0
    while i < len(s):
        j = s.find("{", i)
        if j < 0:
            break
        try:
            obj, end = dec.raw_decode(s[j:])
        except json.JSONDecodeError:
            i = j + 1
            continue
        if isinstance(obj, dict):
            out.append(obj)
        i = j + end
    return out


def _weather_params_from_input(tool_input: str) -> tuple[str, str]:
    objs = _json_objects_in_text(tool_input)
    if not objs:
        return "", ""
    d = objs[0]
    city = str(d.get("city", "")).strip()
    date = str(d.get("date", "")).strip()
    return city, date


def _attraction_params_from_input(tool_input: str) -> tuple[str, str]:
    objs = _json_objects_in_text(tool_input)
    if not objs:
        return "", ""
    for d in reversed(objs):
        if "city" in d and "weather" in d:
            return str(d["city"]).strip(), str(d["weather"]).strip()
    d = objs[-1]
    return str(d.get("city", "")).strip(), str(d.get("weather", "")).strip()


@tool
def get_weather(tool_input: str) -> str:
    """查询指定城市天气。参数为 JSON 字符串，例如 {{"city":"北京"}} 或 {{"city":"北京","date":""}}；仅支持实时天气。"""
    city, date = _weather_params_from_input(tool_input)
    if not city:
        return "天气查询失败：未能从 Action Input 中解析出 city，请使用 JSON，例如 {{\"city\": \"北京\"}}"

    city = city.split("\n")[0].split(" ")[0]

    if date and date.strip():
        return f"提示：当前工具仅支持查询实时天气，无法获取{date} {city}的天气数据。以下是{city}当前天气：\n"

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


@tool
def get_attraction(tool_input: str) -> str:
    """根据城市与天气推荐景点。参数为 JSON 字符串，例如 {{"city":"北京","weather":"阴天"}}。"""
    city, weather = _attraction_params_from_input(tool_input)
    if not city or not weather:
        return (
            "景点推荐失败：未能解析出 city 与 weather。"
            "请使用单行 JSON，例如 {{\"city\": \"北京\", \"weather\": \"阴天\"}}，"
            "且不要在 JSON 后拼接 Observation 或其它文字。"
        )
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        query = f"{city} {weather} 适合去的景点推荐"
        resp = client.search(query=query, include_answer=True)
        answer = resp.get("answer", "未找到相关景点推荐")
        return answer.strip()
    except Exception as e:
        return f"景点推荐失败：{str(e)}"


system_prompt = """
你是旅游助手，用中文思考和回答。可使用以下工具：
{tools}

【防重复调用 — 必须遵守】针对当前这一条 Question 的完整解答过程中：
1. 每个城市：get_weather 最多调用 1 次；get_attraction 最多调用 1 次。
2. 一旦你已经收到该城市的 get_attraction 的 Observation，且其中不以「景点推荐失败」开头，则下一轮只能输出 Final Answer，用中文综合「天气 + 景点」回答用户；禁止再调用 get_weather、get_attraction 或任何工具。
3. 不要认为「需要再确认一次天气」或「英文推荐需要改成中文再查」而重复调用工具；Final Answer 里自行把内容组织成中文即可。
4. 若用户只说「上海呢」「那杭州呢」等，指代与上一轮相同的需求（查天气并推荐景点），对新城市仍遵守上述每城各 1 次的限制。

ReAct 格式说明（标签必须保留英文冒号后的英文前缀，否则无法解析）：
- 每一轮只输出到 Action Input 为止，立刻结束本轮生成。
- 禁止自己写 Observation 行；工具执行后系统会自动插入 Observation: ...

严格按下列模板（Thought / Action / Action Input / Final Answer 为固定英文标签；以下为格式示意，不要照抄其中的「用户的问题」）：

Thought: 用中文写简短推理
Action: 必须是 [{tool_names}] 之一
Action Input: 单行合法 JSON，仅含工具参数，例如 {{"city": "北京"}} 或 {{"city": "北京", "weather": "阴天"}}
（可重复多轮 Thought/Action/Action Input，但须遵守上文「每城每工具最多一次」）
Thought: 我现在知道最终答案了
Final Answer: 用自然语言给用户完整回答

硬性要求：
1. Action Input 必须单行、合法 JSON，键名与工具一致，不要换行、不要用代码块包裹。
2. 输出 Action Input 后不要追加任何内容（不要写 Observation、不要续写工具结果）。

此前对话（无历史则为空，供理解「上海呢」等指代）：
{chat_history}

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

prompt_template = PromptTemplate.from_template(system_prompt)


memory = ConversationBufferMemory(
    memory_key="chat_history",
    # ReAct 文本模板需要字符串历史，不能塞 Message 对象
    # True 的话一般配合MessagesPlaceholder使用，普通字符串配合{chat_history}占位符使用
    return_messages=False,
    # output_key 告诉 Memory 从 lc_agent 的输出中提取哪个字段作为助手的回答存入记忆
    output_key="output",
)

agent = create_react_agent(
    llm=llm,
    prompt=prompt_template,
    tools=[get_weather, get_attraction],
)

agent_executor = AgentExecutor(
    agent=agent,
    memory=memory,
    tools=[get_weather, get_attraction],
    verbose=True,
    handle_parsing_errors="返回到上一步并重新尝试，确保Action Input是有效的JSON格式",
    max_iterations=8,
    early_stopping_method="generate",
    stream_runnable=False,
)
