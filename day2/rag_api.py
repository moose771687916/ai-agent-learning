# -*- coding: utf-8 -*-
"""
知识库问答系统（RAG + FastAPI 接口版）
=================================================

【这个文件干什么】
把 rag_demo.py 的 RAG 能力包装成 HTTP 接口：
别人（或你的前端页面）通过网址发问题，系统查资料并返回"答案 + 来源"。

【和 rag_demo.py 的区别】
- rag_demo.py：问题写死在代码里，跑一次问 3 个问题（命令行版）
- rag_api.py：启动一个服务，别人随时通过网址来问（接口版）

【怎么运行】
    cd D:\AGENTMAKER\ai-learning\day1
    python -m uvicorn rag_api:app --reload
浏览器打开 http://127.0.0.1:8000/docs 测试

【流程】
启动时建库（一次）→ 接口收到问题 → 检索 top2 → 拼 prompt → AI 回答(JSON) → 返回
"""

# ===== 0. 导入 =====
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# ===== 1. 初始化（双平台，和 rag_demo.py 一样） =====
load_dotenv()

# --- 向量化客户端（硅基流动）--- 负责"找资料"
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
EMBED_MODEL = "BAAI/bge-m3"   # 免费开源向量化模型

# --- 对话客户端（智谱）--- 负责"写答案"
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
CHAT_MODEL = "glm-4-flash"    # 永久免费对话模型

# ===== 2. 工具函数：文字 → 向量 =====
def get_embedding(text: str):
    """调用硅基流动的 embedding 接口，把一段文字变成一串数字（向量）"""
    response = embed_client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding

# ===== 3. 工具函数：算两个向量的"相似度" =====
def cosine_similarity(vec_a, vec_b):
    """余弦相似度：衡量两个向量有多"像"，越接近 1 越像"""
    dot = sum(x * y for x, y in zip(vec_a, vec_b))          # 点积
    norm_a = sum(x * x for x in vec_a) ** 0.5               # a 的长度
    norm_b = sum(x * x for x in vec_b) ** 0.5               # b 的长度
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)

# ===== 4. 建库（模块加载时执行一次——这就是"启动时搬家"） =====
# 原始文档：5 块汽车保养知识（手工切好块）
documents = [
    "机油的作用是润滑发动机内部零件、减少磨损、帮助散热。一般建议每行驶5000公里或6个月更换一次机油，以先到者为准。",
    "轮胎胎压过低会增加油耗并加速轮胎磨损，胎压过高则容易爆胎。建议每月检查一次胎压，标准值通常标注在驾驶座门框的贴纸上。",
    "刹车片是车辆安全的关键部件。当刹车片厚度小于3毫米时必须更换，正常使用寿命约3万到5万公里，听到刹车异响时应立即检查。",
    "空调滤芯负责过滤进入车厢的空气，建议每1万公里或一年更换一次。如果空调出风有异味，也应尽早更换空调滤芯。",
    "电瓶（蓄电池）寿命一般在2到4年。冬季冷启动困难、大灯变暗可能是电瓶老化信号，需要到店检测电压和启动电流。",
]

# 向量库：每条 = 原文 + 向量
vector_store = []
for doc in documents:
    vector_store.append({
        "text": doc,
        "vector": get_embedding(doc)   # 调用硅基流动，把这段文字变成向量
    })

print(f"✅ 知识库建好：{len(vector_store)} 块文档，每块 {len(vector_store[0]['vector'])} 维")

# ===== 5. 问答主函数（和 rag_demo.py 的 ask_rag 一模一样） =====
def ask_rag(question: str):
    """RAG 问答：检索 + 拼 prompt + AI 回答（返回 answer + sources）"""

    # 把问题变成向量
    question_vector = get_embedding(question)

    # 检索：算问题和每块文档的相似度，找最像的 2 块
    scored = []
    for item in vector_store:
        score = cosine_similarity(question_vector, item["vector"])
        scored.append((score, item["text"]))

    scored.sort(reverse=True)          # 相似度从高到低排序
    top2 = scored[:2]                  # 取最像的 2 块

    # 把资料拼进 prompt（关键！RAG 的核心动作）
    context = "\n".join(text for _, text in top2)
    system_prompt = f"""
你是一个汽车保养知识助手。请只根据下面提供的资料回答问题，
如果资料里没有相关信息，answer 就写"资料中没有相关内容"，sources 写空列表。
不要编造答案。

请严格按照 JSON 格式输出，不要输出任何其他文字：
{{"answer": "你的回答", "sources": ["依据的资料原文1", "依据的资料原文2"]}}

【资料】
{context}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    # 让 AI 基于资料回答
    response = chat_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.3
    )
    content = response.choices[0].message.content

    # 解析 JSON（AI 不听话时兜底）
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"answer": content, "sources": []}
    return result


# ===== 6. FastAPI 接口层（把函数变成网址） =====
app = FastAPI(title="知识库问答系统（RAG）")

class AskRequest(BaseModel):
    """请求体：别人发 POST 时必须带 question 字段"""
    question: str

@app.get("/")
def home():
    """根路径：告诉访问者怎么用"""
    return {"message": "知识库问答系统已启动，去 /docs 测试吧"}

@app.post("/ask")
def ask(request: AskRequest):
    """
    核心接口：收到问题 → 调 ask_rag → 返回 {answer, sources}
    别人调用方式：POST /ask  body: {"question": "机油多久换一次？"}
    """
    result = ask_rag(request.question)
    return result
