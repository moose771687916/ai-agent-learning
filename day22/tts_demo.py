# -*- coding: utf-8 -*-
"""
Day 22 - TTS让Agent说话！（语音合成！）

耳朵+嘴巴闭环！
  听（ASR识别！）→ 想（LLM！）→ 说（TTS合成！）= 完整语音Agent！

用硅基流动免费TTS模型：FunAudioLLM/CosyVoice2-0.5B！
（OpenAI兼容接口 /v1/audio/speech！）
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

tts_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

print("=" * 60)
print("【TTS语音合成】（文字 → 声音！）")
text = "你好！我是你的AI助手！今天天气怎么样？"

resp = tts_client.audio.speech.create(
    model="FunAudioLLM/CosyVoice2-0.5B",
    voice="FunAudioLLM/CosyVoice2-0.5B:alex",  # 格式：模型:音色！
    input=text,
    response_format="wav",
)

out_path = r"D:\AGENTMAKER\ai-learning\day22\tts_output.wav"
resp.stream_to_file(out_path)
print(f"✅ 合成完成：{out_path}（{os.path.getsize(out_path)}字节）")
print(f"💬 说的内容：{text}")

print("\n" + "=" * 60)
print("🎯 TTS跑通！Agent会说话了！（听→想→说全闭环！）")
