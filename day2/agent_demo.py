# ============================================================
# agent_demo.py — 你的第一个 Agent！
# 结构：🧠 AI（智谱 glm-4-flash） + 🔧 两个工具（查天气/计算器） + 🔁 循环
# 运行：在 day1 目录下执行  python agent_demo.py
# ============================================================

from openai import OpenAI          # 统一调用大模型的库
from dotenv import load_dotenv     # 读 .env 里的 API Key
import os
import json                         # 解析 AI 传回来的工具参数

# ---------- 0. 初始化客户端（和之前一样的套路）----------
load_dotenv()                                    # 读 .env（保险箱）
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),         # 智谱 Key
    base_url="https://open.bigmodel.cn/api/paas/v4"  # 智谱地址
)
MODEL = "glm-4-flash"   # 免费模型，支持工具调用


# ============================================================
# 🔧 第一部分：定义"工具"（就是普通 Python 函数）
# ============================================================

def get_weather(city: str) -> str:
    """工具1：查指定城市的天气（这里是模拟数据，真实项目接天气API）"""
    # 假装这是一个真实的天气数据库
    weather_db = {
        "上海": "明天 32°C，晴",
        "北京": "明天 18°C，多云",
        "广州": "明天 28°C，阵雨",
        "深圳": "明天 30°C，晴转多云",
    }
    return weather_db.get(city, f"暂无{city}的天气数据")


def calculator(expression: str) -> str:
    """工具2：计算数学表达式，如 '32*2'、'100/4'、'(5+3)*2'"""
    # ⚠️ 教学用 eval，真实项目必须用安全解析（如 ast 或专用库），防止代码注入
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错：{e}"


# ============================================================
# 📋 第二部分：工具清单（告诉 AI "你有这些工具可以用"）
# 这是 Function Calling 的核心——AI 看到这份清单，才知道能调什么
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市明天的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：上海、北京、广州"
                    }
                },
                "required": ["city"]   # city 是必填参数
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，支持加减乘除和括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的表达式，例如：'32*2'、'(5+3)*2'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# 工具名 → 函数 的映射表（AI 说"我要调 get_weather"，程序靠这个表找到真正的函数）
tool_map = {
    "get_weather": get_weather,
    "calculator": calculator,
}


# ============================================================
# 🔁 第三部分：Agent 主循环（核心！）
# 逻辑：问 AI → 它要工具就执行 → 结果喂回去 → 再问 → ... → 它给答案就结束
# ============================================================

def run_agent(user_question: str):
    # 初始化对话历史（system 设定人设 + user 是用户问题）
    messages = [
        {
            "role": "system",
            "content": "你是一个智能助手。你可以使用工具查询天气和进行数学计算。"
                       "需要工具时请调用工具，不需要工具时直接回答用户问题。"
                       "回答要简洁。"
        },
        {"role": "user", "content": user_question}
    ]

    max_rounds = 5   # 最多循环 5 轮，防止 AI 死循环（安全锁）

    for round_num in range(max_rounds):
        print(f"\n{'='*50}")
        print(f"🔄 第 {round_num + 1} 轮")
        print(f"{'='*50}")

        # ---------- 第1步：问 AI（带上工具清单 tools）----------
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,          # ★ 关键：把工具清单传给 AI，它才知道能调什么
            temperature=0.1       # 工具调用场景调低，保证稳定
        )
        message = response.choices[0].message   # 取出 AI 的回复

        # ---------- 第2步：判断 AI 是"要工具"还是"给答案"----------
        if message.tool_calls:
            # ★ AI 说："我要调用工具！"
            print(f"\n🤖 AI 决定调用工具：")
            for tc in message.tool_calls:
                print(f"   工具名：{tc.function.name}")
                print(f"   参数：{tc.function.arguments}")

            # 把 AI 的"要工具"消息加进历史（必须，否则下一轮 AI 失忆）
            messages.append({
                "role": message.role,
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # ---------- 第3步：执行 AI 要的每个工具 ----------
            for tc in message.tool_calls:
                func_name = tc.function.name                     # 工具名，如 "get_weather"
                func_args = json.loads(tc.function.arguments)   # 参数（JSON字符串→字典），如 {"city":"上海"}
                func = tool_map[func_name]                       # 从映射表找到真正的函数
                result = func(**func_args)                       # 执行函数！**func_args 把字典拆成参数
                print(f"\n🔧 工具执行结果：{result}")

                # 把工具结果加进历史（role="tool"，这是 OpenAI 规定的特殊角色）
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,     # 必须和上面的 tool_call.id 对应
                    "content": str(result)      # 工具返回的结果
                })

            # 循环继续 → 回到第1步，带着"工具结果"再问 AI
            print("\n➡️  带着工具结果，进入下一轮...")

        else:
            # ★ AI 直接给最终答案了 → 循环结束！
            print(f"\n{'='*50}")
            print(f"✅ 最终回答（第 {round_num + 1} 轮给出）")
            print(f"{'='*50}")
            print(message.content)
            return message.content

    # 超过最大轮数还没给答案（安全兜底）
    print("\n⚠️ 达到最大循环次数，强制结束")
    return None


# ============================================================
# 🚀 第四部分：启动入口
# ============================================================

if __name__ == "__main__":
    # 测试问题：需要"查天气 + 算数"两个工具，AI 会自己决定调几次
    question = "上海明天几度？这个温度换算成华氏度是多少？"
    print(f"👤 你问：{question}")
    run_agent(question)
