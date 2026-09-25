# ============================================================
# agent_with_memory.py — 有记忆的智能助手
# 启动：python -m uvicorn agent_with_memory:app --reload
# 测试：浏览器打开 http://127.0.0.1:8000/docs
# ============================================================

# 导入需要的工具
from openai import OpenAI          # 调用大模型的库
from dotenv import load_dotenv     # 读 .env 里的密码
import os
import json
from datetime import datetime   # ★ 新增：查当前时间用
import random                   # ★ 新增：随机数用                         # 解析 AI 传回来的工具参数

from fastapi import FastAPI         # 做网页接口的库
from pydantic import BaseModel      # 定义请求格式的库


# ============================================================
# 第一部分：准备工作（连接 AI，读密码）
# ============================================================

load_dotenv()   # 读 .env 文件里的 API Key

# 连接智谱（负责对话，当 AI 大脑）
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
CHAT_MODEL = "glm-4-flash"   # 用哪个模型（免费）

# 连接硅基流动（负责向量化，RAG 找资料用）
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
EMBED_MODEL = "BAAI/bge-m3"


# ============================================================
# 第二部分：定义3个工具（就是3个普通 Python 函数）
# ============================================================

# --- 工具1：查天气 ---
def get_weather(city: str) -> str:
    """查某个城市明天的天气"""
    weather_db = {
        "上海": "明天 32°C，晴",
        "北京": "明天 18°C，多云",
        "广州": "明天 28°C，阵雨",
        "深圳": "明天 30°C，晴转多云",
    }
    return weather_db.get(city, f"暂无{city}的天气数据")


# --- 工具2：算数 ---
def calculator(expression: str) -> str:
    """算数学题，比如 '32*1.8+32'"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错：{e}"


# --- 工具4：查当前时间 ---
def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.now()
    return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M:%S')}，{['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]}"


# --- 工具5：生成随机数 ---
def generate_random_number(min: int = 1, max: int = 100) -> str:
    """生成指定范围内的随机整数"""
    result = random.randint(min, max)
    return f"随机数：{result}（范围 {min}~{max}）"


# --- 工具3：RAG 查保养手册（先建向量库）---

# 把文字变成向量（一串数字）
def get_embedding(text: str):
    response = embed_client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding

# 算两个向量有多像
def cosine_similarity(vec_a, vec_b):
    dot = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = sum(x * x for x in vec_a) ** 0.5
    norm_b = sum(x * x for x in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)


# 启动时建一次向量库（5块汽车保养知识）
print("📚 正在建立汽车保养知识向量库...")
documents = [
    "机油...每行驶5000公里或6个月更换...",
    "轮胎胎压...每月检查...",
    "刹车片...厚度小于3毫米时必须更换...",
    "空调滤芯...每1万公里或一年更换...",
    "电瓶...寿命一般在2到4年...",
]
vector_store = []
for doc in documents:
    vector_store.append({"text": doc, "vector": get_embedding(doc)})
print(f"✅ 向量库建好：{len(vector_store)} 块文档")


# RAG 工具：用户问保养问题时，调用这个找资料
def search_maintenance_manual(query: str) -> str:
    query_vector = get_embedding(query)
    scored = []
    for item in vector_store:
        score = cosine_similarity(query_vector, item["vector"])
        scored.append((score, item["text"]))
    scored.sort(reverse=True)
    top2 = scored[:2]
    return "\n---\n".join(text for _, text in top2)


# ============================================================
# 第三部分：工具清单（告诉 AI 有哪些工具可用）
# ============================================================

tools = [
    # 工具1：查天气
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
    # 工具2：算数
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，支持加减乘除和括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "要计算的表达式"}
                },
                "required": ["expression"]
            }
        }
    },
    # 工具3：查保养手册
    {
        "type": "function",
        "function": {
            "name": "search_maintenance_manual",
            "description": "查询汽车保养手册，回答保养、维修、更换周期问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "用户的保养问题"}
                },
                "required": ["query"]
            }
        }
    },
    # 工具4：查当前时间
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期、时间和星期几。当用户问'现在几点''今天几号''今天星期几'时调用。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    # 工具5：生成随机数
    {
        "type": "function",
        "function": {
            "name": "generate_random_number",
            "description": "生成指定范围内的随机整数。当用户要随机数、抽签、掷骰子时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "min": {"type": "integer", "description": "最小值，默认1"},
                    "max": {"type": "integer", "description": "最大值，默认100"}
                },
                "required": []
            }
        }
    }
]

# 把工具名字和真正的函数对应起来
tool_map = {
    "get_weather": get_weather,
    "calculator": calculator,
    "search_maintenance_manual": search_maintenance_manual,
    "get_current_time": get_current_time,
    "generate_random_number": generate_random_number,
}


# ============================================================
# 第四部分：Agent 主循环（AI 的大脑，反复思考直到给出答案）
# ============================================================

def run_agent(messages: list) -> str:
    """
    跑 Agent 循环。
    ★ 注意：这里接收的是 messages 列表（对话历史），不是一个问题字符串。
    外面会把完整的对话历史传进来，这样 AI 就记得之前聊了什么。
    """
    max_rounds = 5   # 最多思考5轮，防止死循环

    for round_num in range(max_rounds):
        print(f"\n🔄 第 {round_num + 1} 轮")

        # 把完整对话历史发给 AI
        response = chat_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,      # ← 传的就是外面传进来的完整历史
            tools=tools,
            temperature=0.1
        )
        message = response.choices[0].message

        # 如果 AI 说要调工具
        if message.tool_calls:
            print(f"   AI 要调工具：{[tc.function.name for tc in message.tool_calls]}")

            # 把 AI 的"要工具"消息加进历史
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

            # 执行每个工具
            for tc in message.tool_calls:
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)
                func = tool_map[func_name]
                result = func(**func_args)
                print(f"   工具结果：{result}")

                # 把工具结果加进历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)
                })

        # 如果 AI 说不需要工具了，直接给答案
        else:
            print(f"   ✅ AI 回答：{message.content}")
            return message.content

    return "抱歉，处理超时了。"


# ============================================================
# 第五部分：网页接口（FastAPI 外壳）
# ============================================================

app = FastAPI(title="智能助手（有记忆版）")


# ★ 记忆的核心：一个大字典，存所有用户的对话历史
# 结构：{ "user1": [对话列表], "user2": [对话列表], ... }
sessions = {}


# 定义用户调接口时要传什么：
# { "session_id": "user1", "question": "上海几度？" }
class ChatRequest(BaseModel):
    session_id: str   # 谁在说话
    question: str     # 说什么


# AI 的系统设定（每次新会话都要带上）
SYSTEM_PROMPT = "你是一个智能助手，可以查询天气、进行数学计算、查询汽车保养手册。需要工具时调用工具，不需要时直接回答。"


@app.post("/chat")
def chat(request: ChatRequest):
    """
    用户调这个接口和 AI 对话。
    request 就是用户传过来的 JSON，里面有 session_id 和 question。
    """

    sid = request.session_id   # 取出用户是谁，比如 "user1"
    print(f"\n👤 用户[{sid}]问：{request.question}")

    # --- 记忆的关键逻辑 ---

    # 第1步：查这个用户有没有来过
    if sid not in sessions:
        # 第一次来：新建一个空对话，只放 system 设定
        sessions[sid] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        print("   🆕 新用户，新建对话")
    else:
        # 之前来过：直接用之前的对话历史
        print(f"   📜 已有历史，共 {len(sessions[sid])} 条消息")

    # 第2步：把用户新说的话加进对话历史
    sessions[sid].append({"role": "user", "content": request.question})

    # 第3步：把完整对话历史（历史+新问题）传给 run_agent
    # AI 看到的就是完整对话，所以记得之前聊了什么
    answer = run_agent(sessions[sid])

    # 第4步：把 AI 的回答也存进历史，下次用户再来就能看到
    sessions[sid].append({"role": "assistant", "content": answer})

    print(f"   💾 已保存，现在共 {len(sessions[sid])} 条消息")

    # 返回结果给用户
    return {"session_id": sid, "question": request.question, "answer": answer}


@app.get("/")
def home():
    return {"message": "有记忆的智能助手已启动（5个工具）", "docs": "打开 /docs 测试"}


# ★ 新增：清除某个用户的对话记忆
@app.delete("/chat/{session_id}")
def clear_memory(session_id: str):
    """清除某个用户的对话历史（相当于重新开始）"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"已清除用户 {session_id} 的对话记忆"}
    else:
        return {"message": f"用户 {session_id} 不存在"}
