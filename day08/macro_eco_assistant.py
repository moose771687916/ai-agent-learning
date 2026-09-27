# ============================================================
# macro_eco_assistant.py - 宏观经济分析助手
# 启动：python -m uvicorn macro_eco_assistant:app --reload
# 页面：http://127.0.0.1:8000/
# ============================================================

from dotenv import load_dotenv
import os
import json
import io

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

import docx
from PyPDF2 import PdfReader

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

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
    model="BAAI/bge-m3"
)

app = FastAPI(title="宏观经济分析助手")

# 向量库
VECTOR_STORE_PATH = "faiss_index"
vector_store = None

# 记忆
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
SYSTEM_PROMPT = """你是一个专业的宏观经济分析助手。
你可以：
1. 搜索上传的宏观经济文档，回答相关问题
2. 用通俗易懂的方式解释宏观经济概念（CPI、GDP、货币政策等）
3. 分析宏观经济数据对股市、债市、汇率的影响

回答时要：
- 基于文档内容回答
- 用通俗易懂的语言
- 分点说明，逻辑清晰
"""


# ============================================================
# 2. RAG工具
# ============================================================

@tool
def search_macro_doc(query: str) -> str:
    """搜索上传的宏观经济文档，回答相关问题"""
    global vector_store
    if vector_store is None:
        return "还没有上传宏观经济文档，请先上传文档。"
    docs = vector_store.similarity_search(query, k=3)
    return "\n---\n".join([doc.page_content for doc in docs])


@tool
def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """查汇率，比如美元兑人民币、欧元兑美元"""
    import requests
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        res = requests.get(url, timeout=5)
        data = res.json()
        rate = data["rates"].get(target_currency)
        if rate:
            return f"1 {base_currency} = {rate} {target_currency}"
        else:
            return f"找不到 {base_currency} 兑 {target_currency} 的汇率"
    except Exception as e:
        return f"查询汇率失败：{str(e)}"


@tool
def search_web(query: str) -> str:
    """搜索网络，获取最新新闻和信息"""
    import requests
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        res = requests.get(url, timeout=5)
        data = res.json()
        results = []
        if data.get("AbstractText"):
            results.append(data["AbstractText"])
        if data.get("RelatedTopics"):
            for topic in data["RelatedTopics"][:3]:
                if topic.get("Text"):
                    results.append(topic["Text"])
        if results:
            return "\n".join(results)
        else:
            return f"没有找到关于 '{query}' 的搜索结果"
    except Exception as e:
        return f"搜索失败：{str(e)}"


# ============================================================
# 3. 创建Agent
# ============================================================

tools = [search_macro_doc, get_exchange_rate, search_web]
agent = create_react_agent(chat_model, tools)


# ============================================================
# 4. API接口
# ============================================================

@app.on_event("startup")
def load_vector_store():
    """启动时从本地加载向量库"""
    global vector_store
    if os.path.exists(VECTOR_STORE_PATH):
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        print(f"已从本地加载宏观经济文档库")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传宏观经济文档（TXT/Word/PDF），自动建知识库"""
    global vector_store
    try:
        filename = file.filename
        content = await file.read()

        if filename.endswith(".txt"):
            text = content.decode("utf-8")
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
        else:
            return {"error": f"不支持的文件格式：{filename}"}

        if not text.strip():
            return {"error": "文件内容是空的"}

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(text)

        vector_store = FAISS.from_texts(chunks, embeddings)
        vector_store.save_local(VECTOR_STORE_PATH)

        return {"message": f"上传成功！{len(chunks)} 块宏观经济文档已建库", "chunks": len(chunks)}
    except Exception as e:
        return {"error": f"上传失败：{str(e)}"}


class ChatRequest(BaseModel):
    session_id: str
    question: str

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


@app.get("/sessions")
def get_sessions():
    return {"sessions": list(sessions.keys())}


@app.get("/chat/{session_id}/history")
def get_history(session_id: str):
    if session_id not in sessions:
        return {"messages": []}
    history = []
    for role, content in sessions[session_id]:
        if role == "human":
            history.append({"role": "user", "content": content})
        elif role == "ai":
            history.append({"role": "ai", "content": content})
    return {"messages": history}


# ============================================================
# 5. 页面
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>宏观经济分析助手</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h2 { text-align: center; color: #1a1b1c; }
            .sid-bar { display: flex; gap: 10px; margin-bottom: 15px; align-items: center; flex-wrap: wrap; }
            .sid-bar input { padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
            .sid-bar select { padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
            .sid-bar button { padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer; }
            .upload-area { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #ddd; }
            .upload-area p { margin: 0 0 10px 0; color: #6b7280; font-size: 13px; }
            .chat-box { background: white; border-radius: 12px; padding: 20px; height: 400px; overflow-y: auto; border: 1px solid #ddd; }
            .msg { margin: 10px 0; padding: 10px 15px; border-radius: 8px; max-width: 85%; line-height: 1.6; white-space: pre-wrap; }
            .user { background: #007bff; color: white; margin-left: auto; }
            .ai { background: #e9e9e9; }
            .input-area { margin-top: 15px; display: flex; gap: 10px; }
            .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
            .input-area button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>📊 宏观经济分析助手</h2>

        <div class="sid-bar">
            <label>账号：</label>
            <input type="text" id="sid" placeholder="输入账号名">
            <select id="sidSelect" onchange="document.getElementById('sid').value=this.value; switchAccount()">
                <option value="">-- 选择已有账号 --</option>
            </select>
            <button onclick="switchAccount()">切换</button>
            <button onclick="clearMem()">清除记忆</button>
        </div>

        <div class="upload-area">
            <p>上传宏观经济文档（TXT/Word/PDF）：</p>
            <input type="file" id="fileInput">
            <button onclick="upload()">上传文档</button>
        </div>

        <div class="chat-box" id="chatBox"></div>

        <div class="input-area">
            <input type="text" id="input" placeholder="问宏观经济相关的问题..." onkeydown="if(event.key==='Enter')send()">
            <button onclick="send()">发送</button>
        </div>

        <script>
            function getSid() { return document.getElementById("sid").value.trim(); }

            async function loadSessions() {
                const res = await fetch("/sessions");
                const data = await res.json();
                const select = document.getElementById("sidSelect");
                select.innerHTML = '<option value="">-- 选择已有账号 --</option>';
                data.sessions.forEach(s => {
                    const opt = document.createElement("option");
                    opt.value = s;
                    opt.textContent = s;
                    select.appendChild(opt);
                });
            }

            async function switchAccount() {
                const sid = getSid();
                if (!sid) { alert("请输入账号名"); return; }
                document.getElementById("chatBox").innerHTML = "";
                const res = await fetch("/chat/" + sid + "/history");
                const data = await res.json();
                data.messages.forEach(msg => {
                    addMsg(msg.content, msg.role === "user");
                });
            }

            async function upload() {
                try {
                    const fileInput = document.getElementById("fileInput");
                    if (!fileInput.files[0]) { alert("请先选择文件"); return; }
                    const formData = new FormData();
                    formData.append("file", fileInput.files[0]);
                    const res = await fetch("/upload", {method: "POST", body: formData});
                    const data = await res.json();
                    alert(data.message || data.error);
                } catch (e) {
                    alert("上传出错：" + e.message);
                }
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
                if (!q) return;
                if (!sid) { alert("请输入账号名"); return; }
                addMsg(q, true);
                input.value = "";
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({session_id: sid, question: q})
                });
                const data = await res.json();
                addMsg(data.answer, false);
                loadSessions();
            }

            async function clearMem() {
                const sid = getSid();
                if (!sid) { alert("请输入账号名"); return; }
                if (!confirm("确定要清除 " + sid + " 的记忆吗？")) return;
                await fetch("/chat/" + sid, {method: "DELETE"});
                document.getElementById("chatBox").innerHTML = "";
                addMsg("已清除记忆", false);
                loadSessions();
            }

            loadSessions();
        </script>
    </body>
    </html>
    """
