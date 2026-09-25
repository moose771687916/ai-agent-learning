# ============================================================
# agent_api.py — Agent 的 FastAPI 接口版（含 RAG 工具）
# 三个工具：查天气 + 计算器 + 查汽车保养手册（RAG）
# 启动：python -m uvicorn agent_api:app --reload
# 测试：浏览器打开  http://127.0.0.1:8000/docs
# ============================================================

from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from fastapi import FastAPI
from pydantic import BaseModel


# ---------- 0. 初始化客户端 ----------
load_dotenv()

# 智谱：对话（AI 大脑）
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
CHAT_MODEL = "glm-4-flash"

# 硅基流动：向量化（RAG 找资料用）
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
EMBED_MODEL = "BAAI/bge-m3"


# ============================================================
# 🔧 第一部分：工具函数（3个工具）
# ============================================================

# ---------- 工具1：查天气 ----------
def get_weather(city: str) -> str:
    weather_db = {
        "上海": "明天 32°C，晴",
        "北京": "明天 18°C，多云",
        "广州": "明天 28°C，阵雨",
        "深圳": "明天 30°C，晴转多云",
    }
    return weather_db.get(city, f"暂无{city}的天气数据")


# ---------- 工具2：计算器 ----------
def calculator(expression: str) -> str:
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错：{e}"


# ---------- 工具3：查汽车保养手册（RAG）----------
# --- RAG 基础函数 ---
def get_embedding(text: str):
    response = embed_client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def cosine_similarity(vec_a, vec_b):
    dot = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = sum(x * x for x in vec_a) ** 0.5
    norm_b = sum(x * x for x in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)


# --- 建库（启动时建一次）---
print("📚 正在建立汽车保养知识向量库...")
documents = [
    "机油的作用是润滑发动机内部零件、减少磨损、帮助散热。一般建议每行驶5000公里或6个月更换一次机油，以先到者为准。",
    "轮胎胎压过低会增加油耗并加速轮胎磨损，胎压过高则容易爆胎。建议每月检查一次胎压，标准值通常标注在驾驶座门框的贴纸上。",
    "刹车片是车辆安全的关键部件。当刹车片厚度小于3毫米时必须更换，正常使用寿命约3万到5万公里，听到刹车异响时应立即检查。",
    "空调滤芯负责过滤进入车厢的空气，建议每1万公里或一年更换一次。如果空调出风有异味，也应尽早更换空调滤芯。",
    "电瓶（蓄电池）寿命一般在2到4年。冬季冷启动困难、大灯变暗可能是电瓶老化信号，需要到店检测电压和启动电流。",
]
vector_store = []
for doc in documents:
    vector_store.append({"text": doc, "vector": get_embedding(doc)})
print(f"✅ 向量库建好：{len(vector_store)} 块文档")


# --- RAG 工具函数：AI 调用这个工具来查保养资料 ---
def search_maintenance_manual(query: str) -> str:
    """查询汽车保养手册，返回最相关的资料内容。
    当用户问保养、维修、更换周期等问题时调用。"""
    # 1. 问题向量化
    query_vector = get_embedding(query)
    # 2. 检索最相关的2块
    scored = []
    for item in vector_store:
        score = cosine_similarity(query_vector, item["vector"])
        scored.append((score, item["text"]))
    scored.sort(reverse=True)
    top2 = scored[:2]
    # 3. 拼成文本返回给 AI
    result_text = "\n---\n".join(text for _, text in top2)
    return result_text


# ============================================================
# 📋 第二部分：工具清单（3个工具）
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市明天的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，例如：上海、北京"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，支持加减乘除和括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "要计算的表达式，例如：'32*1.8+32'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_maintenance_manual",
            "description": "查询汽车保养手册，回答保养、维修、更换周期相关问题。当用户问保养、换机油、刹车片、轮胎、电瓶、空调滤芯等问题时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "用户的保养相关问题，例如：'机油多久换一次'、'刹车片什么时候换'"}
                },
                "required": ["query"]
            }
        }
    }
]

tool_map = {
    "get_weather": get_weather,
    "calculator": calculator,
    "search_maintenance_manual": search_maintenance_manual,
}


# ============================================================
# 🔁 第三部分：Agent 主循环
# ============================================================

def run_agent(user_question: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "你是一个智能助手，可以查询天气、进行数学计算、查询汽车保养手册。"
                       "需要工具时调用工具，不需要时直接回答。回答要简洁准确。"
        },
        {"role": "user", "content": user_question}
    ]

    max_rounds = 5

    for round_num in range(max_rounds):
        print(f"\n{'='*50}")
        print(f"🔄 第 {round_num + 1} 轮")
        print(f"{'='*50}")

        response = chat_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=tools,
            temperature=0.1
        )
        message = response.choices[0].message

        if message.tool_calls:
            print(f"\n🤖 AI 决定调用工具：")
            for tc in message.tool_calls:
                print(f"   工具名：{tc.function.name}")
                print(f"   参数：{tc.function.arguments}")

            messages.append({
                "role": message.role,
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            for tc in message.tool_calls:
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)
                func = tool_map[func_name]
                result = func(**func_args)
                print(f"\n🔧 工具执行结果：{result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)
                })

            print("\n➡️  带着工具结果，进入下一轮...")

        else:
            print(f"\n✅ 最终回答（第 {round_num + 1} 轮）：{message.content}")
            return message.content

    return "抱歉，处理超时了，请换个问题试试。"


# ============================================================
# 🌐 第四部分：FastAPI 外壳
# ============================================================

app = FastAPI(title="智能助手 Agent 接口（含RAG）", version="1.1")


class AgentRequest(BaseModel):
    question: str


@app.post("/chat")
def chat(request: AgentRequest):
    print(f"\n{'='*50}")
    print(f"👤 收到问题：{request.question}")
    print(f"{'='*50}")
    answer = run_agent(request.question)
    return {"question": request.question, "answer": answer}


@app.get("/")
def home():
    return {
        "message": "智能助手 Agent 接口已启动（3个工具：天气/计算器/保养手册）",
        "docs": "访问 /docs 测试",
    }
