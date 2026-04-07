# 智能旅游助手 Agent 

基于 LangChain 框架实现的智能旅游助手 Agent，支持查询指定城市实时天气，并根据天气情况推荐适合游玩的景点。提供 ReAct 与 FunctionCall 两种 Agent 实现模式，可灵活切换。 

## 功能特性 

* 实时天气查询：调用 wttr.in 接口获取指定城市当前天气与温度 - 景点智能推荐：基于 Tavily 搜索引擎，根据城市+天气组合推荐适配景点 - 双 Agent 模式：支持 ReAct 思维链模式和 FunctionCall 工具调用模式 

* 对话记忆：维护会话上下文，支持「上海呢」「那杭州呢」等指代式提问 - 防重复调用：严格限制每个城市的天气/景点查询次数，避免冗余请求 - 前端交互：提供简洁的 Web 界面，支持对话重置、消息发送等基础操作



## 环境配置

### 1.依赖安装

```bash
pip install uv
uv init
uv add langchain langchain-openai langchain-community python-dotenv fastapi uvicorn requests tavily-python pydantic
```

### 2.env文件

具体见：[hello-agents-chapter1-初识智能体 - 知乎](https://zhuanlan.zhihu.com/p/2021372176352252985)

```env
# OpenAI 配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=your-openai-base-url (可选，如自定义代理地址)
MODEL_NAME=coding-glm-4.7-free (或其他支持的模型)

# Tavily 搜索引擎配置
TAVILY_API_KEY=your-tavily-api-key

# Agent 模式：react / functioncall
AGENT_MODE=functioncall
```



## 快速启动

在项目根目录下启动后端服务：

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

浏览器访问localhost:8080即可进入前端交互页面。



## 使用示例

- 基础提问：「上海今天天气怎么样？适合去哪里玩？」
- 指代式提问：在查询完上海后，输入「那杭州呢？」
- 直接查询：「广州晴天适合去的景点」



## 核心文件说明

| 文件               | 功能说明                                                     |
| ------------------ | ------------------------------------------------------------ |
| main.py            | FastAPI 服务入口，加载 Agent 实例，提供聊天 / 重置接口，挂载静态前端页面 |
| lc_react.py        | ReAct 模式 Agent 实现，包含天气 / 景点工具、解析函数、ReAct 提示词模板 |
| lc_functioncall.py | FunctionCall 模式 Agent 实现，基于 Pydantic 定义工具入参，简化参数解析 |
| index.html         | 前端交互页面，支持消息发送、加载状态、对话重置、自适应布局   |



## 未完待续

由于该Agent过于简单，后续还会新增新功能。