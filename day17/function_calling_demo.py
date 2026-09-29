# ============================================================
# day17/function_calling_demo.py - Function Calling原理演示
# 用最原始的方式（OpenAI SDK）！不经过LangChain！
# 让你看清楚大模型到底返回了什么！
# ============================================================

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# ============================================================
# 我们的工具（真正执行的函数！）
# ============================================================

def get_weather(city: str) -> str:
    """查询某个城市的天气"""
    return f"{city}今天晴，25度"


# ============================================================
# 工具定义（告诉大模型：我有这个工具！）
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，比如北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    }
]


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("Function Calling原理演示")
    print("=" * 50)
    
    # 1. 创建客户端
    client = OpenAI(
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 2. 用户提问！
    user_question = "北京天气怎么样？"
    print(f"用户提问：{user_question}")
    print()
    
    # 3. 把问题和工具定义一起发给大模型！
    print("【第1步】把问题和工具定义发给大模型！")
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你有一个工具叫get_weather！当用户询问某个城市的天气时，你必须调用get_weather工具来查询！"},
            {"role": "user", "content": user_question}
        ],
        tools=tools
    )
    
    message = response.choices[0].message
    print("大模型返回：")
    print(f"  content：{message.content}")
    print(f"  tool_calls：{message.tool_calls}")
    print()
    
    # 4. 大模型返回了工具调用请求！
    print("【第2步】大模型返回了工具调用请求！")
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        print(f"  工具名：{tool_call.function.name}")
        print(f"  参数：{tool_call.function.arguments}")
        print()
        
        # 5. 我们真正去执行工具！
        print("【第3步】我们（代码）真正去执行工具！")
        import json
        args = json.loads(tool_call.function.arguments)
        city = args["city"]
        tool_result = get_weather(city)
        print(f"  执行 get_weather({city})")
        print(f"  工具结果：{tool_result}")
        print()
        
        # 6. 把工具结果返回给大模型！
        print("【第4步】把工具结果返回给大模型！")
        messages = [
            {"role": "user", "content": user_question},
            message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            }
        ]
        
        response2 = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            tools=tools
        )
        final_answer = response2.choices[0].message.content
        print(f"大模型最终回答：{final_answer}")
    else:
        print("大模型没有调用工具，直接回答了！")
    
    # 7. 总结！
    print()
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 大模型不会真的执行工具！")
    print("2. 大模型只返回一个工具调用请求（工具名+参数）！")
    print("3. 真正执行工具的是我们（代码）！")
    print("4. 把工具结果返回给大模型！")
    print("5. 大模型根据结果生成最终回答！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
