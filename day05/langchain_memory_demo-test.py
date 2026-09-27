# ============================================================
# langchain_memory_demo.py - LangChain记忆组件演示
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# 1. 定义工具
@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    return f"{expression} = {eval(expression)}"

# 2. 创建Agent，加上记忆组件！
model = ChatOpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-flash",
)

tools = [calculator]

# 关键！加个MemorySaver，框架自动帮你管记忆
memory = MemorySaver()
agent = create_react_agent(model, tools, checkpointer=memory)


# 3. 测试
print("=== LangChain记忆组件演示 ===\n")

config = {"configurable": {"thread_id": "user_123"}}  # thread_id就是session_id

# 第1轮
print("第1轮：用户问 1+1等于几")
result = agent.invoke(
    {"messages": [("human", "1+1等于几")]},
    config=config
)
print(f"AI回答：{result['messages'][-1].content}\n")

# 第2轮——不用传历史！框架自动记住了
print("第2轮：用户问 那再乘以2呢")
result = agent.invoke(
    {"messages": [("human", "那再乘以2呢")]},
    config=config  # 同一个thread_id，框架自动加载历史
)
print(f"AI回答：{result['messages'][-1].content}\n")

print("=== 对比手写版 ===")
print("手写版：你要自己存sessions字典，自己维护messages列表")
print("LangChain版：MemorySaver + thread_id，框架自动帮你存历史")
