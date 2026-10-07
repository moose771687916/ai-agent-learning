# -*- coding: utf-8 -*-
"""
Day 23 - 车载语音助手！（车企方向核心demo！）

这就是"车载Agent"的完整形态：
  👂 听：ASR！（SenseVoiceSmall！语音→文字！）
  🧠 想：LLM！（glm-4-flash！理解 + 决定调哪个工具！）
  🔧 工具：控制车（空调/车窗/导航！）+ 查天气（真实API！Day 8！）
  🗣️ 说：TTS！（CosyVoice2！回答→语音！）

和Day 22的区别：Day 22语音助手"不会调工具"（天气是编的！）
            Day 23语音助手【接上工具】！（车控真的执行！天气真的查！）
→ 这就是"幻觉三解法"里的"接工具"！（Day 22讲过！）
"""

import os
import json
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

# ============ 工具定义（Day 17学的！） ============
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "control_car",
            "description": "控制车辆功能：空调、车窗、导航。用户说开/关空调、调温度、开窗、导航到某地时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["开空调", "关空调", "开窗", "关窗", "开导航"], "description": "要执行的动作"},
                    "target": {"type": "string", "description": "目标参数：温度（如26度）或导航地点（如万达广场）"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市实时天气。用户问天气时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，如北京"}
                },
                "required": ["city"]
            }
        }
    }
]


def control_car(action, target=""):
    """执行车控！（模拟！真实车机通过CAN总线控制！）"""
    if action == "开空调":
        temp = target.replace("度", "") if target else "24"
        return f"✅ 空调已打开，温度设定为{temp}度"
    if action == "关空调":
        return "✅ 空调已关闭"
    if action == "开窗":
        return "✅ 车窗已打开，注意安全"
    if action == "关窗":
        return "✅ 车窗已关闭"
    if action == "开导航":
        return f"✅ 正在规划去{target}的路线"
    return "❌ 暂不支持该操作"


def get_weather(city):
    """真实查天气！（Day 8的和风天气API！）"""
    CITY_IDS = {"北京": "101010100", "上海": "101020100", "广州": "101280101", "深圳": "101280601", "马鞍山": "101220506"}
    loc = CITY_IDS.get(city, "101010100")
    url = f"https://devapi.qweather.com/v7/weather/now?location={loc}&key={os.getenv('QWEATHER_API_KEY')}"
    data = json.loads(urllib.request.urlopen(url).read())
    now = data["now"]
    return f"{city}当前{now['text']}，气温{now['temp']}℃，体感{now['feelsLike']}℃"


def run_tool(name, args):
    if name == "control_car":
        return control_car(args.get("action", ""), args.get("target", ""))
    if name == "get_weather":
        return get_weather(args.get("city", "北京"))
    return "工具不存在"


# ============ 主流程：听 → 想（调工具）→ 说！ ============
print("=" * 60)
print("【车载语音助手：听 → 想（调工具！）→ 说！】")

# ① 听！（ASR！）
audio_path = r"D:\AGENTMAKER\ai-learning\day23\car_voice.wav"
with open(audio_path, "rb") as f:
    question = audio_client.audio.transcriptions.create(
        model="FunAudioLLM/SenseVoiceSmall", file=f
    ).text
print(f"👂 听：司机说 → 「{question}」")

# ② 想！（LLM + 工具调用！多轮！）
messages = [
    {"role": "system", "content": "你是车载语音助手！司机的话你负责调用合适的工具执行！执行完用一句话口语化汇报！"},
    {"role": "user", "content": question}
]
resp = chat_client.chat.completions.create(
    model="glm-4-flash", messages=messages, tools=TOOLS
)
msg = resp.choices[0].message

if msg.tool_calls:
    for tc in msg.tool_calls:
        name = tc.function.name
        args = json.loads(tc.function.arguments)
        result = run_tool(name, args)
        print(f"🔧 调工具：{name}({args}) → {result}")
        messages.append(msg)
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    final = chat_client.chat.completions.create(
        model="glm-4-flash", messages=messages
    ).choices[0].message.content
else:
    final = msg.content
print(f"🧠 想：Agent汇报 → 「{final}」")

# ③ 说！（TTS！）
speech = audio_client.audio.speech.create(
    model="FunAudioLLM/CosyVoice2-0.5B",
    voice="FunAudioLLM/CosyVoice2-0.5B:alex",
    input=final, response_format="wav"
)
out_path = r"D:\AGENTMAKER\ai-learning\day23\car_agent_output.wav"
speech.stream_to_file(out_path)
print(f"🗣️ 说：语音回复 → {out_path}（{os.path.getsize(out_path)}字节）")

print("\n" + "=" * 60)
print("🎯 车载语音助手跑通！听→想→调工具→说！全闭环！")
print("   （和Day 22的区别：接上工具了！不编了！真实执行！）")
