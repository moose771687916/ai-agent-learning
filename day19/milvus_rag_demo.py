# -*- coding: utf-8 -*-
"""
Day 19 - Milvus 真RAG实战（真实embedding！）
流程：真实文档 → BGE-M3(免费embedding模型) → Milvus Lite → 检索！

和上个demo的区别：
  上个demo：手工造"假向量"（模拟embedding）
  这个demo：BGE-M3把文档变成"真向量"（和真实生产一样！）
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pymilvus import MilvusClient

# ============ 0. 加载密钥 ============
# 从 day18/.env 读取（智谱/硅基流动/和风 的key都在里面！）
load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

# 连接硅基流动（免费额度！BGE-M3中文最强开源embedding！）
llm_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

# ============ 1. 定义embedding函数（把文字变成向量！）============
def embed(texts):
    """把 1个或多个文本 变成向量（1024维）"""
    resp = llm_client.embeddings.create(
        model="BAAI/bge-m3",   # 免费的中文embedding模型！
        input=texts
    )
    return [item.embedding for item in resp.data]


# ============ 2. 准备真实文档（模拟你的知识库！）============
docs = [
    "新能源汽车电池采用磷酸铁锂技术，循环寿命超过2000次，续航可达600公里",
    "车载智能座舱支持语音控制、手势识别，可自动规划导航路线",
    "固态电池是下一代电池技术，能量密度比液态电池提升40%以上",
    "自动驾驶系统依赖激光雷达、摄像头、毫米波雷达多传感器融合",
    "充电桩分为交流慢充和直流快充，直流快充30分钟可充80%电量",
    "AI大模型通过海量数据预训练，具备强大的语言理解和生成能力",
    "LangChain是AI应用开发框架，提供链式调用、Agent、RAG等能力",
    "RAG检索增强生成：先从知识库检索相关资料，再让大模型生成回答",
]

print("=" * 55)
print("【第1步】用BGE-M3把8篇文档变成向量（1024维）")
doc_vectors = embed(docs)   # 8篇文档 → 8个1024维向量！
print(f"✅ 完成！8篇文档 → 8个向量，每个{len(doc_vectors[0])}维")


# ============ 3. 连接Milvus + 建集合 ============
print("\n【第2步】连接Milvus，建集合（dimension=1024！）")
client = MilvusClient("milvus_rag.db")   # 本地数据库文件！

COLLECTION = "rag_docs"
if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)

client.create_collection(
    collection_name=COLLECTION,
    dimension=1024           # 必须和BGE-M3输出维度一致！
)
print(f"✅ 集合 '{COLLECTION}' 创建成功（维度=1024，匹配BGE-M3！）")


# ============ 4. 插入：向量 + 原文 一起存！ ============
print("\n【第3步】插入数据（向量+原文！）")
data = []
for i, (text, vec) in enumerate(zip(docs, doc_vectors)):
    data.append({
        "id": i + 1,
        "vector": vec,        # BGE-M3生成的真向量！
        "text": text          # 原文（检索后返回给大模型！）
    })

client.insert(collection_name=COLLECTION, data=data)
print(f"✅ 已插入 {len(data)} 篇文档（向量+原文）")


# ============ 5. 检索：问题 → embedding → 找最像的！ ============
print("\n【第4步】检索演示")
print("-" * 55)

# 用户问题！（真实场景：用户在对话里问的！）
question = "电动车充电要多久？"

# 问题也变成向量！
query_vec = embed([question])[0]

# 去Milvus找最像的3篇！
results = client.search(
    collection_name=COLLECTION,
    data=[query_vec],
    limit=3,
    output_fields=["text"]   # 把原文带出来！
)

print(f"用户问题：『{question}』")
print(f"检索到最相关的3篇：\n")
for i, hit in enumerate(results[0]):
    print(f"  #{i+1} 相似度={hit['distance']:.4f}")
    print(f"      原文: {hit['entity']['text']}")
    print()

print("=" * 55)
print("🎯 这就是完整RAG：问题→向量→检索→原文→（下一步给大模型生成回答！）")
print("   下一篇文档/问题都能查！知识库=这些文档！")
