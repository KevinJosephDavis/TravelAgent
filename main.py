import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


def _load_agent_executor():
    mode = os.getenv("AGENT_MODE", "react").strip().lower()
    if mode == "react":
        from lc_agent.lc_react import agent_executor as executor
    elif mode == "functioncall":
        from lc_agent.lc_functioncall import agent_executor as executor
    else:
        raise RuntimeError(
            "Invalid AGENT_MODE. Expected 'react' or 'functioncall', "
            f"got '{mode}'."
        )
    return executor, mode


agent_executor, agent_mode = _load_agent_executor()
logger.info("Loaded agent mode: %s", agent_mode)

# ======================= 导入 LangGraph 助手 =======================
try:
    from lg_agent.graph import travel_agent  
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph agent not available")

# ======================= FastAPI 应用 =======================
app = FastAPI(title="MyTravelAgent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================= 数据模型 =======================
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    reply: str


# ======================= 原有 LangChain 接口 =======================
@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    try:
        result = agent_executor.invoke({"input": body.message.strip()})
        output = result.get("output") or ""
        return ChatResponse(reply=str(output).strip() or "（助手未返回内容）")
    except Exception as e:
        logger.exception("agent_executor.invoke failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/chat/reset")
async def reset_chat():
    try:
        agent_executor.memory.clear()
    except Exception:
        pass
    return {"ok": True}


# ======================= 新增：LangGraph 旅游助手接口 =======================
@app.post("/api/travel", response_model=ChatResponse)
async def travel_agent_chat(body: ChatRequest):
    if not LANGGRAPH_AVAILABLE:
        raise HTTPException(status_code=500, detail="LangGraph 不可用")

    try:
        # 配置记忆会话ID
        import uuid
        memory_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": memory_id}}
        result = travel_agent.invoke({
            "user_input": body.message.strip(),
            "user_preferences": {},
            "interrupt_needed": True,
            "is_complete": True,
            "retry_count": 0
        }, config=config)

        # 从state里取结果
        reply = result.get("output") or "✅ 旅游助手执行完成！"
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.exception("travel_agent.invoke failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ======================= 静态文件前端 =======================
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")