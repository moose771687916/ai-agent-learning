# -*- coding: utf-8 -*-
"""
Day 22 - 完整多模态Agent！（整合版！一个程序！全能力！）

这是"完整产品形态"：一个多模态助手！支持【文字/图片/语音】三种输入！

能力清单：
  👁️ 看图：glm-4v-flash！（图片→描述/问答！）
  👂 听声：SenseVoiceSmall！（语音→文字！）
  🧠 思考：glm-4-flash！（LLM！）
  🗣️ 说话：CosyVoice2！（文字→语音！）
  🔍 找图：多模态RAG！（文字→检索图片！）

演示3个场景（真实产品用例！）：
  A. 看图问答！（用户发图+提问！）
  B. 语音对话！（用户语音→回答→语音回复！）
  C. 图片检索！（文字找图！）
"""

import os
import urllib.request
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
audio_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)


# ============ 能力模块 ============
def see_image(image_url, question):
    """看图！（glm-4v-flash！）"""
    resp = chat_client.chat.completions.create(
        model="glm-4v-flash",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }]
    )
    return resp.choices[0].message.content


def hear_audio(audio_path):
    """听声！（SenseVoiceSmall！）"""
    with open(audio_path, "rb") as f:
        resp = audio_client.audio.transcriptions.create(
            model="FunAudioLLM/SenseVoiceSmall",
            file=f
        )
    return resp.text


def think(question, system="你是多模态AI助手！回答要自然、简洁。"):
    """思考！（glm-4-flash！）"""
    return chat_client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ]
    ).choices[0].message.content


def speak(text, out_path):
    """说话！（CosyVoice2！）"""
    speech = audio_client.audio.speech.create(
        model="FunAudioLLM/CosyVoice2-0.5B",
        voice="FunAudioLLM/CosyVoice2-0.5B:alex",
        input=text,
        response_format="wav",
    )
    speech.stream_to_file(out_path)
    return out_path


def embed(texts):
    resp = audio_client.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [v.embedding for v in resp.data]


# ============ 场景A：看图问答！ ============
print("=" * 60)
print("【场景A：看图问答！】（用户发图 + 提问！）")
img_a = "https://aka.doubaocdn.com/s/3srAxLZ6UP"   # 红圆图！
ans_a = see_image(img_a, "这张图里有什么形状？什么颜色？")
print(f"🖼️ 用户发图 + 问「有什么形状颜色？」")
print(f"🤖 Agent回答：{ans_a}")

# ============ 场景B：语音对话闭环！（听→想→说！） ============
print("\n" + "=" * 60)
print("【场景B：语音对话！】（用户语音 → 回答 → 语音回复！）")
audio_path = r"D:\AGENTMAKER\ai-learning\day22\test_audio.wav"
if not os.path.exists(audio_path):
    urllib.request.urlretrieve("https://aka.doubaocdn.com/s/YcTfTXjQ5e", audio_path)
q_b = hear_audio(audio_path)
print(f"👂 听到用户说：{q_b}")
ans_b = think(q_b, "你是车载语音助手！回答简短口语化！")
print(f"🧠 思考出回答：{ans_b}")
out_b = speak(ans_b, r"D:\AGENTMAKER\ai-learning\day22\full_agent_b.wav")
print(f"🗣️ 语音回复已生成：{out_b}")

# ============ 场景C：图片检索！（多模态RAG！） ============
print("\n" + "=" * 60)
print("【场景C：图片检索！】（文字找图！多模态RAG！）")
image_lib = [
    {"name": "img_circle.png",     "url": "https://aka.doubaocdn.com/s/3srAxLZ6UP"},
    {"name": "img_square.png",     "url": "https://aka.doubaocdn.com/s/6UZJmu7RgP"},
    {"name": "img_twocircles.png", "url": "https://aka.doubaocdn.com/s/b3GpIUVdAz"},
]
store = []
for img in image_lib:
    desc = see_image(img["url"], "用一句话描述：什么形状？什么颜色？")
    store.append({"name": img["name"], "desc": desc,
                  "vec": embed([desc])[0]})
    print(f"  📦 入库：{img['name']} → {desc}")

import math
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) + 1e-9)

query = "蓝色的方形"
qv = embed([query])[0]
top = max(store, key=lambda x: cos(qv, x["vec"]))
print(f"🔍 用户找「{query}」 → 最像: {top['name']}（{cos(qv, top['vec']):.3f}）→ {top['desc']}")

print("\n" + "=" * 60)
print("🎯 完整多模态Agent！三种输入（文字/图/声）三种能力（看/听/说/找）全通！")
print("   这就是企业多模态助手的形态：多模态输入 → 理解 → 多模态输出！")
