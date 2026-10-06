# -*- coding: utf-8 -*-
"""
Day 19 - 真Milvus Server + 完整6环节RAG！（企业形态！）

流程：①读文档 → ②切块 → ③embedding → ④存【真Server】→ ⑤检索 → ⑥生成回答
对比milvus_full_rag.py：数据从Lite(.db文件) → 真Server(Docker容器)！
API完全一样！只改连接方式 + 加flush！
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pymilvus import MilvusClient

load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)


def embed(texts):
    """文字 → 1024维向量（BGE-M3免费）"""
    resp = embed_client.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [item.embedding for item in resp.data]


# ============ ①读文档 ============
def read_doc(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ============ ②切块 ============
def chunk_text(text, chunk_size=200):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


DOC_PATH = r"D:\AGENTMAKER\ai-learning\day08\CPI基础知识.txt"
COLLECTION = "cpi_kb_server"

print("=" * 55)
print("【① 读文档】")
full_text = read_doc(DOC_PATH)
print(f"✅ 读取文档：CPI基础知识.txt（共{len(full_text)}字）")

print("\n【② 切块】")
chunks = chunk_text(full_text, chunk_size=200)
print(f"✅ 切成 {len(chunks)} 块（每块约200字）")

print("\n【③ embedding】")
chunk_vectors = embed(chunks)
print(f"✅ {len(chunks)}块 → BGE-M3 → 每块1024维向量")

print("\n【④ 存【真Milvus Server】】")
# ⚠️ 唯一区别！连接【服务器】！（不是.db文件！）
client = MilvusClient("http://localhost:19530")
print("✅ 连接真Server：http://localhost:19530（Docker容器！）")
if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)
client.create_collection(collection_name=COLLECTION, dimension=1024)
data = [
    {"id": i + 1, "vector": vec, "text": chunk}
    for i, (chunk, vec) in enumerate(zip(chunks, chunk_vectors))
]
client.insert(collection_name=COLLECTION, data=data)
client.flush(COLLECTION)          # ⚠️ Server版必须flush！（Lite自动！）
print(f"✅ 存入真Server：{len(data)}块（向量+原文）+ flush落盘！")

print("\n【⑤ 检索】")
question = "CPI太低会发生什么？"
query_vec = embed([question])[0]
client.load_collection(COLLECTION)
results = client.search(
    collection_name=COLLECTION,
    data=[query_vec],
    limit=3,
    output_fields=["text"]
)
contexts = []
print(f"✅ 检索到最相关的{len(results[0])}块：")
for hit in results[0]:
    contexts.append(hit["entity"]["text"])
    print(f"  相似度={hit['distance']:.4f} | {hit['entity']['text'][:45]}...")

print("\n【⑥ 生成回答】")
context = "\n\n".join(contexts)
resp = chat_client.chat.completions.create(
    model="glm-4-flash",
    messages=[
        {
            "role": "system",
            "content": "你是知识库助手，只能根据提供的资料回答用户问题。资料中没有的内容，回答'资料中未提及'。"
        },
        {
            "role": "user",
            "content": f"参考资料：\n{context}\n\n用户问题：{question}"
        }
    ]
)
answer = resp.choices[0].message.content
print(f"✅ 智谱GLM-4生成回答：\n\n{answer}")

print("\n" + "=" * 55)
print("🎯 真Milvus Server + 完整6环节RAG 闭环成功！")
print("   数据存在Docker服务器！任何程序都能连！这就是企业形态！")
