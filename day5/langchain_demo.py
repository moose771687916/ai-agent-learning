# ============================================================
# langchain_demo.py - LangChain版Agent（对比手写版）
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

# 1. 定义工具（就写个函数+@tool装饰器，比手写版简单多了）
@tool
def calculator(expression: str) -> str:
    """计算数学表达式，比如 32*1.8+32"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错：{e}"

@tool
def get_weather(city: str) -> str:
    """查询某个城市的天气"""
    weather_db = {
        "上海": "32°C，晴",
        "北京": "18°C，多云",
        "当涂": "21°C，雾",
    }
    return weather_db.get(city, f"暂无{city}的天气数据")

# 2. 连接大模型
model = ChatOpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-flash",
    temperature=0.1
)

# 3. 创建Agent（一行代码！）
tools = [calculator, get_weather]
agent = create_react_agent(model, tools)

# 4. 测试
print("=== LangChain版Agent ===")
question = "上海几度？另外帮我算一下 32*1.8+32 等于多少"
print(f"用户问：{question}")

result = agent.invoke({"messages": [("human", question)]})
print(f"AI回答：{result['messages'][-1].content}")
