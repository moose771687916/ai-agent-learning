# -*- coding: utf-8 -*-
"""
Day 22 - 完整语音Agent！（听 → 想 → 说！全闭环！）

这就是语音助手的核心架构（小爱同学/天猫精灵的原理！）：
  ① 听：ASR！（SenseVoiceSmall！语音 → 文字！）
  ② 想：LLM！（glm-4-flash！文字 → 回答！）
  ③ 说：TTS！（CosyVoice2！回答 → 语音！）

全程免费API！三个模型接力完成！
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

# 用户语音（之前生成的！"帮我查一下北京今天的天气怎么样"！）
AUDIO_URL = "https://aka.doubaocdn.com/s/YcTfTXjQ5e"
AUDIO_PATH = r"D:\AGENTMAKER\ai-learning\day22\test_audio.wav"

print("=" * 60)
print("【完整语音Agent：听 → 想 → 说！】")

# ① 听！（ASR！语音 → 文字！）
if not os.path.exists(AUDIO_PATH):
    urllib.request.urlretrieve(AUDIO_URL, AUDIO_PATH)
with open(AUDIO_PATH, "rb") as f:
    asr_resp = audio_client.audio.transcriptions.create(
        model="FunAudioLLM/SenseVoiceSmall",
        file=f
    )
question = asr_resp.text
print(f"👂 听：用户说 → 「{question}」")

# ② 想！（LLM！文字 → 回答！）
answer = chat_client.chat.completions.create(
    model="glm-4-flash",
    messages=[
        {"role": "system", "content": "你是车载语音助手！回答要简短、口语化、像说话一样自然。"},
        {"role": "user", "content": question}
    ]
).choices[0].message.content
print(f"🧠 想：Agent想 → 「{answer}」")

# ③ 说！（TTS！回答 → 语音！）
speech = audio_client.audio.speech.create(
    model="FunAudioLLM/CosyVoice2-0.5B",
    voice="FunAudioLLM/CosyVoice2-0.5B:alex",
    input=answer,
    response_format="wav",
)
out_path = r"D:\AGENTMAKER\ai-learning\day22\voice_agent_output.wav"
speech.stream_to_file(out_path)
print(f"🗣️ 说：合成语音 → {out_path}（{os.path.getsize(out_path)}字节）")

print("\n" + "=" * 60)
print("🎯 完整语音Agent闭环成功！（听→想→说全通！这就是语音助手的原理！）")
