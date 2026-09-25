# ============================================================
# agent_demo_simple.py — 完全展开版（不用任何简写，每步都打印）
# 适合初学者看懂 Agent 循环的每一个细节
# 运行：python agent_demo_simple.py
# ============================================================

from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
MODEL = "glm-4-flash"


# ---------- 工具函数 ----------
def get_weather(city: str) -> str:
    weather_db = {
        "上海": "明天 32°C，晴",
        "北京": "明天 18°C，多云",
    }
    return weather_db.get(city, f"暂无{city}的数据")


def calculator(expression: str) -> str:
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错：{e}"


# ---------- 工具清单 ----------
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
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "数学表达式"}},
                "required": ["expression"]
            }
        }
    }
]

tool_map = {"get_weather": get_weather, "calculator": calculator}


# ============================================================
# 主函数：完全展开版
# ============================================================
def run_agent(user_question: str):

    # ========== 第0步：初始化 messages 列表 ==========
    messages = [
        {"role": "system", "content": "你是智能助手，可以用工具查天气和算数。需要工具时调用工具，不需要时直接回答。"},
        {"role": "user", "content": user_question}
    ]
    print("\n" + "="*60)
    print("【初始化】messages 里有 2 条消息：")
    for i, m in enumerate(messages):
        print(f"  [{i}] role={m['role']}, content={m['content'][:30]}...")
    print("="*60)

    max_rounds = 5

    # ========== 开始循环 ==========
    for round_num in range(max_rounds):
        print(f"\n{'#'*60}")
        print(f"# 第 {round_num + 1} 轮开始")
        print(f"# 此时 messages 里有 {len(messages)} 条消息")
        print(f"{'#'*60}")

        # ---------- 第1步：问 AI ----------
        print("\n【第1步】把 messages + tools 发给 AI...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            temperature=0.1
        )
        message = response.choices[0].message
        print(f"  AI 回复：content={message.content}")
        print(f"  AI 回复：tool_calls={message.tool_calls}")

        # ---------- 第2步：判断 AI 要工具还是给答案 ----------
        if message.tool_calls:
            print("\n【第2步】AI 说要调工具！开始处理...")

            # ============================================================
            # ★ 关键：把 message 对象转成字典，加进 messages
            # （这里完全展开，不用列表推导式）
            # ============================================================

            # 2a. 先建一个空列表，用来装 tool_calls 字典
            tool_calls_list = []
            print(f"\n【2a】建空列表 tool_calls_list = []")

            # 2b. 遍历 AI 要调的每个工具，逐个拼成字典，加进列表
            print(f"【2b】遍历 message.tool_calls（有 {len(message.tool_calls)} 个工具调用）")
            for tc in message.tool_calls:
                print(f"  处理一个工具调用：")
                print(f"    id = {tc.id}")
                print(f"    name = {tc.function.name}")
                print(f"    arguments = {tc.function.arguments}")

                # 拼成标准字典
                one_tool_call_dict = {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                print(f"    拼成字典：{one_tool_call_dict}")

                # 加进列表
                tool_calls_list.append(one_tool_call_dict)
                print(f"    加进 tool_calls_list，现在列表有 {len(tool_calls_list)} 个元素")

            print(f"\n【2c】tool_calls_list 最终 = {tool_calls_list}")

            # 2d. 建一条完整的 assistant 消息字典
            assistant_message_dict = {
                "role": message.role,
                "content": message.content,
                "tool_calls": tool_calls_list    # ★ 就是上面拼好的列表
            }
            print(f"\n【2d】建 assistant 消息字典：")
            print(f"  role = {assistant_message_dict['role']}")
            print(f"  content = {assistant_message_dict['content']}")
            print(f"  tool_calls = {assistant_message_dict['tool_calls']}")

            # 2e. 加进 messages
            messages.append(assistant_message_dict)
            print(f"\n【2e】messages.append(assistant_message_dict)")
            print(f"  现在 messages 有 {len(messages)} 条消息")

            # ============================================================
            # 第3步：执行每个工具
            # ============================================================
            print(f"\n【第3步】执行 AI 要调的每个工具...")
            for tc in message.tool_calls:
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)
                print(f"  执行工具：{func_name}，参数：{func_args}")

                func = tool_map[func_name]
                result = func(**func_args)
                print(f"  工具返回：{result}")

                # 建一条 tool 消息字典，加进 messages
                tool_message_dict = {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)
                }
                messages.append(tool_message_dict)
                print(f"  加进 messages，现在有 {len(messages)} 条消息")

            print(f"\n【本轮结束】带着工具结果，进入下一轮...")

        else:
            # ---------- AI 直接给答案了 ----------
            print(f"\n【第2步】AI 没有要工具，直接给答案了！")
            print(f"\n{'='*60}")
            print(f"✅ 最终回答（第 {round_num + 1} 轮给出）：")
            print(f"   {message.content}")
            print(f"{'='*60}")
            return message.content

    print("\n⚠️ 达到最大循环次数，强制结束")
    return None


# ========== 启动 ==========
if __name__ == "__main__":
    question = "上海明天几度？这个温度换算成华氏度是多少？"
    print(f"👤 你问：{question}")
    run_agent(question)
