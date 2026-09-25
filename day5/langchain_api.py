# ============================================================
# langchain_api.py - LangChain版Agent + FastAPI + 持久化记忆
# 启动：python -m uvicorn langchain_api:app --reload
# 聊天页面：http://127.0.0.1:8000/chat
# ============================================================

from dotenv import load_dotenv
import os
import json
from datetime import datetime
import random
import requests

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from openai import OpenAI as OpenAIClient

load_dotenv()

# ============================================================
# 1. 准备工作
# ============================================================

chat_model = ChatOpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-flash",
    temperature=0.1
)

embed_client = OpenAIClient(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
EMBED_MODEL = "BAAI/bge-m3"


# ============================================================
# 2. 定义工具（@tool装饰器）
# ============================================================

@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气情况"""
    qweather_key = os.getenv("QWEATHER_API_KEY")
    qweather_host = "p84wcwk7vm.re.qweatherapi.com"
    try:
        city_url = f"https://{qweather_host}/geo/v2/city/lookup?location={city}&key={qweather_key}"
        city_resp = requests.get(city_url, timeout=5).json()
        if city_resp.get("code") != "200":
            return f"找不到城市：{city}"
        city_id = city_resp["location"][0]["id"]
        weather_url = f"https://{qweather_host}/v7/weather/now?location={city_id}&key={qweather_key}"
        weather_resp = requests.get(weather_url, timeout=5).json()
        now = weather_resp["now"]
        return f"{city}：{now['text']}，{now['temp']}°C，体感{now['feelsLike']}°C，湿度{now['humidity']}%"
    except Exception as e:
        return f"查天气失败：{e}"

@tool
def calculator(expression: str) -> str:
    """计算数学表达式，比如 32*1.8+32"""
    try:
        return f"{expression} = {eval(expression)}"
    except Exception as e:
        return f"计算出错：{e}"

@tool
def get_current_time() -> str:
    """获取当前日期、时间和星期几"""
    now = datetime.now()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M:%S')}，{weekdays[now.weekday()]}"

@tool
def generate_random_number(min: int = 1, max: int = 100) -> str:
    """生成指定范围内的随机整数"""
    result = random.randint(min, max)
    return f"随机数：{result}（范围 {min}~{max}）"


# ============================================================
# 3. RAG工具（向量库持久化）
# ============================================================

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

VECTOR_STORE_FILE = "vector_store.json"
documents = [
    "机油...每行驶5000公里或6个月更换...",
    "轮胎胎压...每月检查...",
    "刹车片...厚度小于3毫米时必须更换...",
    "空调滤芯...每1万公里或一年更换...",
    "电瓶...寿命一般在2到4年...",
]

if os.path.exists(VECTOR_STORE_FILE):
    with open(VECTOR_STORE_FILE, "r", encoding="utf-8") as f:
        vector_store = json.load(f)
    print(f"从文件加载向量库：{len(vector_store)} 块文档")
else:
    print("第一次建向量库...")
    vector_store = []
    for doc in documents:
        vector_store.append({"text": doc, "vector": get_embedding(doc)})
    with open(VECTOR_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(vector_store, f, ensure_ascii=False)
    print(f"向量库建好：{len(vector_store)} 块文档")

@tool
def search_maintenance_manual(query: str) -> str:
    """查询汽车保养手册，回答保养、维修、更换周期问题"""
    query_vector = get_embedding(query)
    scored = []
    for item in vector_store:
        score = cosine_similarity(query_vector, item["vector"])
        scored.append((score, item["text"]))
    scored.sort(reverse=True)
    top2 = scored[:2]
    return "\n---\n".join(text for _, text in top2)


# ============================================================
# 4. 创建Agent（一行代码！）
# ============================================================

tools = [get_weather, calculator, search_maintenance_manual, get_current_time, generate_random_number]
agent = create_react_agent(chat_model, tools)


# ============================================================
# 5. 持久化记忆
# ============================================================

app = FastAPI(title="LangChain版AI助手")

SESSIONS_FILE = "sessions.json"

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_sessions():
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

sessions = load_sessions()
print(f"从文件加载了 {len(sessions)} 个用户的对话历史")

SYSTEM_PROMPT = "你是一个智能助手，可以查询天气、进行数学计算、查询汽车保养手册、查时间、生成随机数。需要工具时调用工具，不需要时直接回答。"


class ChatRequest(BaseModel):
    session_id: str
    question: str


# ============================================================
# 6. API接口
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):
    sid = request.session_id
    if sid not in sessions:
        sessions[sid] = [("system", SYSTEM_PROMPT)]

    sessions[sid].append(("human", request.question))

    result = agent.invoke({"messages": sessions[sid]})
    answer = result["messages"][-1].content

    sessions[sid].append(("ai", answer))
    save_sessions()
    return {"answer": answer}


@app.delete("/chat/{session_id}")
def clear_memory(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        save_sessions()
    return {"message": "已清除记忆"}


@app.get("/chat/{session_id}")
def get_history(session_id: str):
    if session_id in sessions:
        history = [msg for msg in sessions[session_id] if msg[0] in ("human", "ai")]
        return {"messages": history}
    return {"messages": []}


@app.get("/sessions")
def list_sessions():
    return {"users": list(sessions.keys())}


# ============================================================
# 7. 聊天页面
# ============================================================

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>LangChain版AI助手</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h2 { text-align: center; color: #333; }
            .sid-bar { display: flex; gap: 10px; margin-bottom: 15px; align-items: center; }
            .sid-bar label { font-size: 14px; color: #666; }
            .sid-bar input { padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
            .sid-bar select { padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
            .sid-bar button { padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
            .chat-box { background: white; border-radius: 12px; padding: 20px; height: 450px; overflow-y: auto; border: 1px solid #ddd; }
            .msg { margin: 10px 0; padding: 10px 15px; border-radius: 8px; max-width: 80%; line-height: 1.5; }
            .user { background: #007bff; color: white; margin-left: auto; }
            .ai { background: #e9e9e9; }
            .input-area { margin-top: 15px; display: flex; gap: 10px; }
            .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            .input-area button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>LangChain版AI助手</h2>
        <div class="sid-bar">
            <label>账号：</label>
            <input type="text" id="sid" placeholder="输入账号ID" value="test1">
            <select id="sidList" onchange="document.getElementById('sid').value=this.value; loadHistory()">
                <option value="">-- 选择已有账号 --</option>
            </select>
            <button onclick="clearMem()">清除记忆</button>
        </div>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-area">
            <input type="text" id="input" placeholder="输入问题，回车发送..." onkeydown="if(event.key==='Enter')send()">
            <button onclick="send()">发送</button>
        </div>
        <script>
            function getSid() { return document.getElementById("sid").value.trim(); }

            async function loadUsers() {
                const res = await fetch("/sessions");
                const data = await res.json();
                const sel = document.getElementById("sidList");
                sel.innerHTML = "<option value=''>-- 选择已有账号 --</option>";
                data.users.forEach(u => {
                    const opt = document.createElement("option");
                    opt.value = u; opt.textContent = u;
                    sel.appendChild(opt);
                });
            }

            async function loadHistory() {
                const sid = getSid();
                if (!sid) return;
                document.getElementById("chatBox").innerHTML = "";
                const res = await fetch("/chat/" + sid);
                const data = await res.json();
                data.messages.forEach(msg => {
                    addMsg(msg[1], msg[0] === "human");
                });
            }

            function addMsg(text, isUser) {
                const div = document.createElement("div");
                div.className = "msg " + (isUser ? "user" : "ai");
                div.textContent = text;
                document.getElementById("chatBox").appendChild(div);
                document.getElementById("chatBox").scrollTop = 99999;
            }

            async function send() {
                const input = document.getElementById("input");
                const q = input.value.trim();
                const sid = getSid();
                if (!q || !sid) return;
                addMsg(q, true);
                input.value = "";
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({session_id: sid, question: q})
                });
                const data = await res.json();
                addMsg(data.answer, false);
                loadUsers();
            }

            async function clearMem() {
                const sid = getSid();
                if (!sid) return;
                if (!confirm("确定要清除 " + sid + " 的所有对话记忆吗？")) return;
                await fetch("/chat/" + sid, {method: "DELETE"});
                document.getElementById("chatBox").innerHTML = "";
                addMsg("已清除记忆", false);
                loadUsers();
            }

            loadUsers();
            loadHistory();
        </script>
    </body>
    </html>
    """
