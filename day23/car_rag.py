# -*- coding: utf-8 -*-
"""
Day 23 - 车载RAG！（车机"懂"车主手册！）

场景：新手司机问车机"仪表盘黄灯亮啥意思？"→ 车机查手册 → 回答！
本质：Day 19学的6环节RAG！（读→切→向量→存→检索→LLM回答！）
应用场景：车主手册问答、维修知识库、售后客服！车企标配！

全程免费！（BGE-M3向量 + glm-4-flash回答！）
"""

import os
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

# ============ ① 车载手册（模拟车机内置知识库！） ============
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

# ============ ② 切块（按空行分段！手册条目！） ============
def chunk_manual(text):
    chunks = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().split("\n")
        title = lines[0]
        for line in lines[1:]:
            if line.strip():
                chunks.append(f"{title}：{line.strip()}")
    return chunks

chunks = chunk_manual(MANUAL)
print(f"📚 手册切块完成：{len(chunks)}条知识！")

# ============ ③ 向量化 + ④ 存（列表当简易向量库！） ============
def embed(texts):
    resp = embed_client.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [v.embedding for v in resp.data]

vecs = embed(chunks)
kb = list(zip(chunks, vecs))

def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) + 1e-9)

# ============ ⑤ 检索 + ⑥ LLM回答 ============
def ask_car(question):
    qv = embed([question])[0]
    ranked = sorted(kb, key=lambda x: -cos(qv, x[1]))
    top3 = [r[0] for r in ranked[:3]]
    context = "\n".join(top3)
    answer = chat_client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是车载助手！只根据用户手册内容回答！简洁口语化！手册里没有的就说'手册里没有这个信息，建议联系4S店'。"},
            {"role": "user", "content": f"用户手册内容：\n{context}\n\n问题：{question}"}
        ]
    ).choices[0].message.content
    return answer, top3

print("=" * 60)
print("【车载RAG测试】新手司机问车机！")
tests = [
    "仪表盘有个黄色的灯亮了，什么意思？",
    "我这车多久保养一次？",
    "冬天车窗起雾怎么除雾？",
]
for q in tests:
    ans, top3 = ask_car(q)
    print(f"\n❓ 问：{q}")
    print(f"🤖 答：{ans}")
    print(f"   📄 检索到：{top3[0][:40]}...")

print("\n" + "=" * 60)
print("🎯 车载RAG跑通！车机'懂手册'！新手问题秒答！")
