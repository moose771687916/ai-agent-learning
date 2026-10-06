# -*- coding: utf-8 -*-
"""
Day 19 - 完整6环节RAG（亲手实现！不用LangChain！）

流程：①读文档 → ②切块 → ③embedding → ④存Milvus → ⑤检索 → ⑥生成回答

知识库：day08/CPI基础知识.txt（宏观经济知识！）
模型：硅基流动BGE-M3（embedding免费！）+ 智谱GLM-4-flash（对话免费！）
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pymilvus import MilvusClient

# ============ 加载密钥（两个平台的Key都在.env里！） ============
load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

# ① embedding客户端（硅基流动！把文字变向量！）
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

# ② 对话客户端（智谱！负责最终生成回答！）
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)


def embed(texts):
    """文字 → 1024维向量（BGE-M3免费模型）"""
    resp = embed_client.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [item.embedding for item in resp.data]


# ============ ①读文档 ============
def read_doc(path):
    """把txt文件读进来，返回全文"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ============ ②切块 ============
def chunk_text(text, chunk_size=200):
    """长文档 → 切成小块！（每块约200字，防止单块太长/太短影响检索）"""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if chunk.strip():          # 跳过空块！
            chunks.append(chunk)
    return chunks


DOC_PATH = r"D:\AGENTMAKER\ai-learning\day08\CPI基础知识.txt"
COLLECTION = "cpi_kb"              # Milvus集合名！

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

print("\n【④ 存Milvus】")
client = MilvusClient("milvus_full_rag.db")   # 数据库文件！
if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)        # demo习惯：清空重建（保证干净）！
client.create_collection(collection_name=COLLECTION, dimension=1024)
data = [
    {"id": i + 1, "vector": vec, "text": chunk}
    for i, (chunk, vec) in enumerate(zip(chunks, chunk_vectors))
]
client.insert(collection_name=COLLECTION, data=data)
print(f"✅ 存入Milvus：{len(data)}块（向量+原文）")

print("\n【⑤ 检索】")
question = "CPI太高对股市有什么影响？"
query_vec = embed([question])[0]              # 问题也变向量！
results = client.search(
    collection_name=COLLECTION,
    data=[query_vec],
    limit=3,                                  # 取最像的3块！
    output_fields=["text"]
)
contexts = []
print(f"✅ 检索到最相关的{len(results[0])}块：")
for hit in results[0]:
    contexts.append(hit["entity"]["text"])    # 收集原文（给大模型当参考资料！）
    print(f"  相似度={hit['distance']:.4f} | {hit['entity']['text'][:45]}...")

print("\n【⑥ 生成回答】")
context = "\n\n".join(contexts)               # 3块原文拼起来 = 参考资料！
resp = chat_client.chat.completions.create(
    model="glm-4-flash",                      # 智谱免费对话模型！
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
print("🎯 完整RAG闭环！①读文档→②切块→③embedding→④存Milvus→⑤检索→⑥生成！")
print("   全部亲手实现！没用LangChain！这就是企业生产代码的样子！")
