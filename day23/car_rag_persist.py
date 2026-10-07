# -*- coding: utf-8 -*-
"""
Day 23 - 车载RAG持久化版！（FAISS存文件！重启还能查！）

升级点（对比car_rag.py）：
  内存列表（程序一关就没了！）→ FAISS索引文件（存磁盘！重启还能查！）

真实车载方案：手册建一次库！存车机本地文件！以后只查询！（离线秒答！）
  + 云端OTA更新手册！（新车型/新功能下发！）

FAISS：Meta出的本地向量库！（Day 19学的！）文件形式！离线可用！
"""

import os
import json
import math
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

import faiss
import numpy as np

# 文件位置（车机本地存储！）
INDEX_FILE = r"D:\AGENTMAKER\ai-learning\day23\car_kb.faiss"
CHUNKS_FILE = r"D:\AGENTMAKER\ai-learning\day23\car_chunks.json"

MANUAL = """
【仪表盘警示灯】
黄色警示灯亮起代表车辆有需要关注的问题：
- 发动机故障灯（像小发动机图标）：可能是发动机系统故障，建议尽快检查。
- 胎压报警灯（像感叹号在轮胎里）：轮胎气压过低，请及时充气。
- ABS防抱死灯（ABS字样）：制动防抱死系统异常，请谨慎驾驶并尽快维修。
- 保养提醒灯（像扳手图标）：到了保养里程，请预约保养。
红色警示灯亮起代表紧急问题，应立即停车检查。

【保养周期】
- 常规保养：每5000公里或6个月一次（先到为准）。
- 大保养：每40000公里或3年一次。
- 保养内容包括：更换机油、机滤、检查刹车片、轮胎、电瓶等。
- 空气滤芯建议每20000公里更换。

【空调使用】
- 自动空调：按下AUTO键，设定目标温度（如26度），系统自动调节风量和温度。
- 冬季除雾：开启除雾模式（扇形图标），同时开启空调压缩机效果更好。
- 夏季制冷：先开内循环快速降温，再切外循环换气。
- 后排空调：部分车型后排有独立空调控制面板。

【安全提示】
- 上车第一件事：系好安全带，调整座椅和后视镜。
- 儿童乘车必须使用儿童安全座椅，不要抱在怀里。
- 行车中不要使用手机，需要操作中控请用语音助手。
- 雨天行车：打开雾灯，降低车速，保持安全距离。

【导航功能】
- 语音导航：说"导航到XX"，车机自动规划路线。
- 实时路况：导航会显示拥堵路段，建议提前绕行。
- 新能源车：导航会自动规划充电站（快充/慢充）。
- 到达目的地前500米，车机会语音提醒。
"""


def embed(texts):
    resp = embed_client.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [v.embedding for v in resp.data]


def chunk_manual(text):
    chunks = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().split("\n")
        title = lines[0]
        for line in lines[1:]:
            if line.strip():
                chunks.append(f"{title}：{line.strip()}")
    return chunks


# ============ 建库（只在第一次跑！） ============
if not os.path.exists(INDEX_FILE):
    print("📦 第一次运行：建库！（切块→向量→存FAISS文件！）")
    chunks = chunk_manual(MANUAL)
    vecs = embed(chunks)

    # FAISS索引（内积！归一化后=余弦相似度！）
    dim = len(vecs[0])
    index = faiss.IndexFlatIP(dim)
    norm = np.array(vecs) / np.linalg.norm(np.array(vecs), axis=1, keepdims=True)
    index.add(norm.astype("float32"))
    faiss.write_index(index, INDEX_FILE)          # 索引存文件！
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)  # 知识原文存文件！
    print(f"✅ 建库完成！{len(chunks)}条知识 → {INDEX_FILE}（{os.path.getsize(INDEX_FILE)}字节！）")
else:
    print("🔄 重启运行：直接加载FAISS文件！（不用重新embedding！秒开！）")

# ============ 查询（每次都能查！） ============
index = faiss.read_index(INDEX_FILE)              # 从文件加载索引！
with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)                         # 从文件加载知识原文！

print("=" * 60)
print("【车载RAG持久化测试】重启后还能查！")
tests = ["仪表盘有个黄色的灯亮了，什么意思？", "多久保养一次？", "冬天除雾怎么办？"]
for q in tests:
    qv = embed([q])[0]
    qn = np.array(qv).astype("float32").reshape(1, -1)
    qn = qn / np.linalg.norm(qn)
    scores, idxs = index.search(qn, 3)            # FAISS检索！（3条！）
    top3 = [chunks[i] for i in idxs[0]]
    context = "\n".join(top3)
    answer = chat_client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是车载助手！只根据用户手册内容回答！简洁口语化！手册里没有的就说'手册里没有这个信息，建议联系4S店'。"},
            {"role": "user", "content": f"用户手册内容：\n{context}\n\n问题：{q}"}
        ]
    ).choices[0].message.content
    print(f"\n❓ 问：{q}")
    print(f"🤖 答：{answer}")
    print(f"   📄 FAISS相似度：{[round(float(s), 3) for s in scores[0]]}")

print("\n" + "=" * 60)
print("🎯 持久化版跑通！知识存在文件里！重启还能查！这就是车载本地RAG！")
