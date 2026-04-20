# 初始化 LLM

from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()

def init_llm() -> ChatOpenAI:
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        temperature=0,
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=30
    )
    return llm