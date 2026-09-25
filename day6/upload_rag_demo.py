# ============================================================
# upload_rag_demo.py - 上传文档建RAG + 有记忆
# 启动：python -m uvicorn upload_rag_demo:app --reload
# 页面：http://127.0.0.1:8000/
# ============================================================

from dotenv import load_dotenv
import os
import json
import io

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI as OpenAIClient

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

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

embed_client = OpenAIClient(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
EMBED_MODEL = "BAAI/bge-m3"

app = FastAPI(title="上传文档建RAG")

# 向量库存文档和向量
vector_store = []

# 记忆：sessions字典
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
SYSTEM_PROMPT = "你是一个文档助手，可以搜索上传的文档回答问题。需要工具时调用工具。"


# ============================================================
# 2. 工具函数
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


# ============================================================
# 3. RAG工具
# ============================================================

@tool
def search_document(query: str) -> str:
    """搜索上传的文档，回答相关问题"""
    if not vector_store:
        return "还没有上传文档，请先上传文档。"
    query_vector = get_embedding(query)
    scored = []
    for item in vector_store:
        score = cosine_similarity(query_vector, item["vector"])
        scored.append((score, item["text"]))
    scored.sort(reverse=True)
    top3 = scored[:3]
    return "\n---\n".join(text for _, text in top3)


# ============================================================
# 4. 创建Agent
# ============================================================

tools = [search_document]
agent = create_react_agent(chat_model, tools)


# ============================================================
# 5. API接口
# ============================================================

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件（TXT/Word/PDF），自动建知识库"""
    filename = file.filename
    content = await file.read()

    # 根据文件类型读内容
    if filename.endswith(".txt"):
        text = content.decode("utf-8")
    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])
    elif filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join([page.extract_text() for page in reader.pages])
    else:
        return {"error": "只支持TXT、Word、PDF文件"}

    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    global vector_store
    vector_store = []
    for chunk in chunks:
        vector_store.append({
            "text": chunk,
            "vector": get_embedding(chunk)
        })
    return {"message": f"上传成功！{len(chunks)} 块文档已建库", "chunks": len(chunks)}


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


# ============================================================
# 6. 页面
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>上传文档建RAG</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h2 { text-align: center; }
            .sid-bar { display: flex; gap: 10px; margin-bottom: 15px; align-items: center; }
            .sid-bar input { padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
            .sid-bar button { padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer; }
            .upload-area { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #ddd; }
            .chat-box { background: white; border-radius: 12px; padding: 20px; height: 350px; overflow-y: auto; border: 1px solid #ddd; }
            .msg { margin: 10px 0; padding: 10px 15px; border-radius: 8px; max-width: 80%; line-height: 1.5; }
            .user { background: #007bff; color: white; margin-left: auto; }
            .ai { background: #e9e9e9; }
            .input-area { margin-top: 15px; display: flex; gap: 10px; }
            .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
            .input-area button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>上传文档建RAG</h2>

        <div class="sid-bar">
            <label>账号：</label>
            <input type="text" id="sid" value="test1">
            <button onclick="clearMem()">清除记忆</button>
        </div>

        <div class="upload-area">
            <input type="file" id="fileInput">
            <button onclick="upload()">上传文档</button>
        </div>

        <div class="chat-box" id="chatBox"></div>

        <div class="input-area">
            <input type="text" id="input" placeholder="问文档相关的问题..." onkeydown="if(event.key==='Enter')send()">
            <button onclick="send()">发送</button>
        </div>

        <script>
            function getSid() { return document.getElementById("sid").value.trim(); }

            async function upload() {
                const fileInput = document.getElementById("fileInput");
                if (!fileInput.files[0]) { alert("请先选择文件"); return; }
                const formData = new FormData();
                formData.append("file", fileInput.files[0]);
                const res = await fetch("/upload", {method: "POST", body: formData});
                const data = await res.json();
                alert(data.message);
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
            }

            async function clearMem() {
                const sid = getSid();
                if (!sid) return;
                if (!confirm("确定要清除 " + sid + " 的记忆吗？")) return;
                await fetch("/chat/" + sid, {method: "DELETE"});
                document.getElementById("chatBox").innerHTML = "";
                addMsg("已清除记忆", false);
            }
        </script>
    </body>
    </html>
    """
