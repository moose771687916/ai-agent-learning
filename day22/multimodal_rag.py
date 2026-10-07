# -*- coding: utf-8 -*-
"""
Day 22 - 多模态RAG实战！（图片也能检索！）

流程（"图生文"检索法！实用！免费！）：
① 每张图 → glm-4v-flash生成【文字描述】！（视觉→文字！）
② 描述 → BGE-M3 → 向量！（和文字RAG一样！）
③ 用户文字查询 → 向量 → 余弦相似度 → 返回最像的图+描述！

本质：把"图片"翻译成"文字"再进向量库！
（企业实用做法：不用专门训练图文模型！直接用视觉模型+文字向量库！）
"""

import os
import math
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

# 图片库（3张测试图！）
IMAGES = [
    {"name": "img_circle.png",      "url": "https://aka.doubaocdn.com/s/3srAxLZ6UP"},
    {"name": "img_square.png",      "url": "https://aka.doubaocdn.com/s/6UZJmu7RgP"},
    {"name": "img_twocircles.png",  "url": "https://aka.doubaocdn.com/s/b3GpIUVdAz"},
]


def describe_image(url):
    """图片 → 文字描述！（glm-4v-flash！）"""
    resp = chat_client.chat.completions.create(
        model="glm-4v-flash",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "用一句话描述这张图片：有什么形状？什么颜色？"},
                {"type": "image_url", "image_url": {"url": url}}
            ]
        }]
    )
    return resp.choices[0].message.content


def embed(texts):
    resp = embed_client.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [v.embedding for v in resp.data]


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) + 1e-9)


print("=" * 60)
print("【多模态RAG建库】每张图 → 描述 → 向量！")
image_store = []
for img in IMAGES:
    desc = describe_image(img["url"])
    vec = embed([desc])[0]
    image_store.append({"name": img["name"], "desc": desc, "vec": vec})
    print(f"🖼️ {img['name']}: {desc}")

print("\n【多模态RAG检索】用户用文字找图！")
queries = ["红色圆形", "蓝色的方形", "两个圆形", "紫色的圆"]
for q in queries:
    qv = embed([q])[0]
    ranked = sorted(image_store, key=lambda x: -cos(qv, x["vec"]))
    top = ranked[0]
    print(f"\nQ: 「{q}」 → 最像: {top['name']}（相似度{cos(qv, top['vec']):.3f}）")
    print(f"   描述: {top['desc']}")

print("\n" + "=" * 60)
print("🎯 多模态RAG跑通！图片能按'意思'被文字检索到！")
