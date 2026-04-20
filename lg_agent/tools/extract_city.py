# 从用户的输入中，提取出城市名称

from lg_agent.tools.init_llm import init_llm
from lg_agent.prompts.prompt import EXTRACT_CITY_PROMPT

def extract_city(user_input: str) -> str:
    """
    从用户输入里抽取出用户想要查询信息的城市名称
    :param user_input: 用户输入的字符串
    :return: 城市名称字符串
    """

    prompt = EXTRACT_CITY_PROMPT.format(user_input=user_input)
    print(prompt)
    # TODO : 这里先直接返回固定值，后续接入 llm 来真正抽取
    # llm = init_llm()
    # response = llm.invoke(prompt)
    # city = response.content.strip()

    return "北京"