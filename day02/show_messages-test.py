# ============================================================
# show_messages.py — 演示：append 之后 messages 到底长什么样
# 运行：python show_messages.py
# ============================================================

import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

# 简化版工具清单
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市明天的天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名"}},
                "required": ["city"]
            }
        }
    }
]

# ========== 初始 messages（2条）==========
messages = [
    {"role": "system", "content": "你是智能助手，可以用工具查天气。需要工具时调用工具。"},
    {"role": "user", "content": "请调用工具查询上海市明天的天气情况"}
]

print("=" * 60)
print("【append 之前】messages 有 2 条：")
print("=" * 60)
print(json.dumps(messages, ensure_ascii=False, indent=2))

# ========== 问 AI ==========
response = client.chat.completions.create(
    model="glm-4-flash",
    messages=messages,
    tools=tools,
    temperature=0.1
)
message = response.choices[0].message

print("\n" + "=" * 60)
print("AI 回复：")
print(f"  content = {message.content}")
print(f"  tool_calls = {message.tool_calls}")
print("=" * 60)

# ========== 第一个 for 循环：把对象拼成字典 ==========
if message.tool_calls:
    tool_calls_list = []
    for tc in message.tool_calls:
        one_dict = {
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            }
        }
        tool_calls_list.append(one_dict)

    print("\n" + "=" * 60)
    print("【第一个 for 循环后】tool_calls_list =")
    print("=" * 60)
    print(json.dumps(tool_calls_list, ensure_ascii=False, indent=2))

    # ========== 建 assistant 消息字典 ==========
    assistant_message = {
        "role": "assistant",
        "content": message.content,
        "tool_calls": tool_calls_list
    }

    # ========== append 进 messages ==========
    messages.append(assistant_message)

    print("\n" + "=" * 60)
    print("【append 之后】messages 有 3 条：")
    print("=" * 60)
    print(json.dumps(messages, ensure_ascii=False, indent=2))
