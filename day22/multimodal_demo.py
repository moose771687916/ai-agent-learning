# -*- coding: utf-8 -*-
"""
Day 22 - 多模态Agent！（能看图！能听声音！）

三个能力（全部免费API！）：
① 看图：智谱glm-4v-flash！（免费多模态大模型！图片URL → 描述！）
② 听声：硅基流动SenseVoiceSmall！（免费ASR语音识别！音频 → 文字！）
③ 综合：语音问题 → 转文字 → LLM回答！（多模态Agent雏形！）

多模态Agent的本质：
  眼睛（视觉模型！）+ 耳朵（ASR！）+ 大脑（LLM！）= 多模态Agent！
"""

import os
import urllib.request
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

# 对话/视觉用智谱！
chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
# 语音识别用硅基流动！
asr_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

# 测试素材URL（本地生成！）
IMAGE_URL = "https://aka.doubaocdn.com/s/W5gdTRzuto"   # 红圆蓝方块绿三角！
AUDIO_URL = "https://aka.doubaocdn.com/s/YcTfTXjQ5e"   # "帮我查一下北京今天的天气怎么样？"


# ============ ① 看图（glm-4v-flash！） ============
def see_image():
    print("=" * 60)
    print("【① 看图】（glm-4v-flash！图片URL → 描述！）")
    resp = chat_client.chat.completions.create(
        model="glm-4v-flash",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "描述这张图片里有什么？按形状和颜色说。"},
                {"type": "image_url", "image_url": {"url": IMAGE_URL}}
            ]
        }]
    )
    print(f"🖼️ 模型描述：{resp.choices[0].message.content}")


# ============ ② 听声（SenseVoiceSmall！） ============
def hear_audio():
    print("\n" + "=" * 60)
    print("【② 听声】（SenseVoiceSmall！音频 → 文字！）")
    # 先下载音频到本地！（ASR接口要文件！）
    audio_path = r"D:\AGENTMAKER\ai-learning\day22\test_audio.wav"
    urllib.request.urlretrieve(AUDIO_URL, audio_path)
    print(f"✅ 下载音频：{audio_path}")
    with open(audio_path, "rb") as f:
        resp = asr_client.audio.transcriptions.create(
            model="FunAudioLLM/SenseVoiceSmall",
            file=f
        )
    print(f"🎧 识别出的文字：{resp.text}")


# ============ ③ 综合：语音 → 文字 → 回答！（多模态Agent雏形！） ============
def multimodal_agent():
    print("\n" + "=" * 60)
    print("【③ 多模态Agent雏形】（语音问题 → 转文字 → LLM回答！）")
    # 听！→ 文字
    audio_path = r"D:\AGENTMAKER\ai-learning\day22\test_audio.wav"
    if not os.path.exists(audio_path):
        urllib.request.urlretrieve(AUDIO_URL, audio_path)
    with open(audio_path, "rb") as f:
        asr_resp = asr_client.audio.transcriptions.create(
            model="FunAudioLLM/SenseVoiceSmall",
            file=f
        )
    question = asr_resp.text
    print(f"🎧 用户语音说：{question}")
    # 想！（LLM回答！）
    answer = chat_client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是AI助手！回答用户问题！"},
            {"role": "user", "content": question}
        ]
    )
    print(f"🧠 Agent回答：{answer.choices[0].message.content}")


see_image()
hear_audio()
multimodal_agent()
print("\n" + "=" * 60)
print("🎯 Day 22 多模态Agent三连跑通！")
