# ============================================================
# demo_for_append.py — 纯模拟，不调用 API
# 一步一步展示：for 循环 → tool_calls_list → append → messages
# ============================================================
import json

# ========== 模拟：API 返回的 message.tool_calls ==========
# （真实场景里这是 API 返回的对象，这里用字典模拟）
message_tool_calls = [
    {
        "id": "call_1",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": "{\"city\": \"上海\"}"
        }
    }
]

# ========== 初始 messages（2条）==========
messages = [
    {"role": "system", "content": "你是智能助手"},
    {"role": "user", "content": "上海明天几度？"}
]

print("=" * 60)
print("【第1步】message.tool_calls 是什么？（API 返回的）")
print("=" * 60)
print(json.dumps(message_tool_calls, ensure_ascii=False, indent=2))

# ========== 第2步：for 循环，逐个拼成字典 ==========
print("\n" + "=" * 60)
print("【第2步】for 循环：逐个取出，拼成纯字典")
print("=" * 60)

tool_calls_list = []    # 先建一个空列表

for tc in message_tool_calls:
    print(f"\n  取出一个 tc:")
    print(f"    id = {tc['id']}")
    print(f"    name = {tc['function']['name']}")
    print(f"    arguments = {tc['function']['arguments']}")

    # 拼成一个纯字典
    one_dict = {
        "id": tc["id"],
        "type": "function",
        "function": {
            "name": tc["function"]["name"],
            "arguments": tc["function"]["arguments"]
        }
    }
    print(f"  拼成纯字典: {one_dict}")

    # 加进 tool_calls_list
    tool_calls_list.append(one_dict)
    print(f"  加进 tool_calls_list，现在有 {len(tool_calls_list)} 个元素")

# ========== 第3步：tool_calls_list 最终 ==========
print("\n" + "=" * 60)
print("【第3步】for 循环跑完后，tool_calls_list =")
print("=" * 60)
print(json.dumps(tool_calls_list, ensure_ascii=False, indent=2))

# ========== 第4步：append，用 tool_calls_list ==========
print("\n" + "=" * 60)
print("【第4步】messages.append，tool_calls 字段用 tool_calls_list")
print("=" * 60)

messages.append({
    "role": "assistant",
    "content": None,
    "tool_calls": tool_calls_list    # ←★ 就是上面 for 循环生成的！
})

print("  append 完成！")

# ========== 第5步：append 之后的 messages ==========
print("\n" + "=" * 60)
print("【第5步】append 之后的完整 messages（3条）：")
print("=" * 60)
print(json.dumps(messages, ensure_ascii=False, indent=2))

# ========== 关键对比 ==========
print("\n" + "=" * 60)
print("【关键对比】")
print("=" * 60)
print("第3条消息里的 tool_calls 字段内容：")
print(json.dumps(messages[2]["tool_calls"], ensure_ascii=False, indent=2))
print("\nfor 循环生成的 tool_calls_list：")
print(json.dumps(tool_calls_list, ensure_ascii=False, indent=2))
print("\n→ 两者完全一样！tool_calls 字段的值就是 for 循环生成的！")
