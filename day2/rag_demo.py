# -*- coding: utf-8 -*-
"""
RAG 最小实现 —— 让 AI 学会"查资料再回答"
=================================================

【这个文件干什么】
实现一个完整的 RAG：先存一份"汽车保养知识"文档进向量库，
然后用户提问时，程序先检索相关段落，再让大模型基于资料回答。
（升级版：答案带"来源"，能溯源到具体是哪块文档）

【用到的东西（都是你学过的）】
1. 硅基流动 BGE-M3：把文字变成向量（找资料用，免费）
2. 余弦相似度：找"和问题最像"的文档块（手写公式，不用装库）
3. 智谱 glm-4-flash：看了资料再回答（免费）
4. JSON 结构化输出：让 AI 返回 {"answer": 答案, "sources": [来源]}

【怎么运行】
    python rag_demo.py

【流程对照图】
阶段一(建库)：文档 → 切块 → 向量化 → 存列表
阶段二(问答)：问题 → 向量化 → 检索 → 拼prompt → AI回答(JSON)
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# ===== 0. 初始化 =====
# 双平台分工：
#   硅基流动 BGE-M3 → 负责"找资料"（向量化，免费）
#   智谱 glm-4-flash → 负责"写答案"（对话，免费）
load_dotenv()

# --- 向量化客户端（硅基流动） ---
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
EMBED_MODEL = "BAAI/bge-m3"   # 免费开源向量化模型

# --- 对话客户端（智谱） ---
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
CHAT_MODEL = "glm-4-flash"    # 永久免费对话模型


# ===== 1. 工具函数：文字 → 向量 =====
def get_embedding(text: str):
    """调用硅基流动的 embedding 接口，把一段文字变成一串数字（向量）"""
    response = embed_client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    # response.data[0].embedding 就是那串数字（1024 个）
    return response.data[0].embedding


# ===== 2. 工具函数：算两个向量的"相似度" =====
def cosine_similarity(vec_a, vec_b):
    """
    余弦相似度：衡量两个向量有多"像"。
    公式：a·b / (|a| × |b|)，结果范围 0~1，越接近 1 越像。
    这是手写版，不依赖任何库。
    """
    dot = sum(x * y for x, y in zip(vec_a, vec_b))          # 点积
    norm_a = sum(x * x for x in vec_a) ** 0.5               # a 的长度
    norm_b = sum(x * x for x in vec_b) ** 0.5               # b 的长度
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)


# ============================================================
# 阶段一：建资料库（搬家，只做一次）
# ============================================================

# 1) 原始文档：假装是"公司内部维修保养手册"的一段内容
documents = [
    "机油的作用是润滑发动机内部零件、减少磨损、帮助散热。一般建议每行驶5000公里或6个月更换一次机油，以先到者为准。",
    "轮胎胎压过低会增加油耗并加速轮胎磨损，胎压过高则容易爆胎。建议每月检查一次胎压，标准值通常标注在驾驶座门框的贴纸上。",
    "刹车片是车辆安全的关键部件。当刹车片厚度小于3毫米时必须更换，正常使用寿命约3万到5万公里，听到刹车异响时应立即检查。",
    "空调滤芯负责过滤进入车厢的空气，建议每1万公里或一年更换一次。如果空调出风有异味，也应尽早更换空调滤芯。",
    "电瓶（蓄电池）寿命一般在2到4年。冬季冷启动困难、大灯变暗可能是电瓶老化信号，需要到店检测电压和启动电流。",
]

# 2) 切块 + 向量化 + 存进"向量库"（这里用简单的列表模拟向量数据库）
# 每一条记录 = {"text": 原文, "vector": 向量}
vector_store = []
for doc in documents:
    vector_store.append({
        "text": doc,
        "vector": get_embedding(doc)   # 调用智谱，把这段文字变成向量
    })

print(f"✅ 资料库建好了：共 {len(vector_store)} 块文档，每块向量 {len(vector_store[0]['vector'])} 维")


# ============================================================
# 阶段二：问答（每次提问都走一遍）
# ============================================================

def ask_rag(question: str):
    """RAG 问答主函数：检索 + 拼 prompt + AI 回答（返回 JSON 结构）"""

    # ---- ④ 把问题也变成向量 ----
    question_vector = get_embedding(question)

    # ---- ⑤ 检索：算问题和每块文档的相似度，找最像的 2 块 ----
    scored = []
    for item in vector_store:
        score = cosine_similarity(question_vector, item["vector"])
        scored.append((score, item["text"]))

    scored.sort(reverse=True)          # 相似度从高到低排序
    top2 = scored[:2]                  # 取最像的 2 块
    print(f"\n📎 检索到最相关的资料（相似度）:")
    for score, text in top2:
        print(f"   {score:.3f}  {text[:30]}...")

    # ---- ⑥ 把资料拼进 prompt（关键！RAG 的核心动作） ----
    context = "\n".join(text for _, text in top2)  # 拼资料
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

    # ---- ⑦ 让 AI 基于资料回答 ----
    response = chat_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.3  # 回答偏稳定
    )
    content = response.choices[0].message.content

    # ---- ⑧ 把 AI 返回的 JSON 字符串解析成 Python 字典 ----
    # AI 返回的是字符串 '{"answer": "...", "sources": [...]}'，
    # json.loads 把它变成能直接取值的字典。
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # 万一 AI 不听话没输出纯 JSON，就兜底：整段当答案，来源留空
        result = {"answer": content, "sources": []}
    return result


# ===== 测试：问几个问题 =====
if __name__ == "__main__":
    # 问题1：资料里有 → 应该回答准确
    print("\n" + "=" * 50)
    print("问题：机油多久换一次？")
    print("=" * 50)
    r = ask_rag("机油多久换一次？")
    print("AI回答：", r["answer"])
    print("来源：", r["sources"])

    # 问题2：资料里有 → 应该回答准确
    print("\n" + "=" * 50)
    print("问题：刹车片什么时候需要更换？")
    print("=" * 50)
    r = ask_rag("刹车片什么时候需要更换？")
    print("AI回答：", r["answer"])
    print("来源：", r["sources"])

    # 问题3：资料里没有 → 应该回答"资料中没有"而不是瞎编
    print("\n" + "=" * 50)
    print("问题：发动机正时皮带什么时候换？")
    print("=" * 50)
    r = ask_rag("发动机正时皮带什么时候换？")
    print("AI回答：", r["answer"])
    print("来源：", r["sources"])
