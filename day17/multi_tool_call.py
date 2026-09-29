# ============================================================
# day17/multi_tool_call.py - 多工具调用演示（改进版）
# 加循环！处理多轮工具调用！
# ============================================================

from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()

# ============================================================
# 我们的工具（真正执行的函数！）
# ============================================================

def get_weather(city: str) -> str:
    """查询某个城市的天气"""
    return f"{city}今天晴，25度"

def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except:
        return "计算错误"


# ============================================================
# 工具定义
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气情况！当用户询问任何城市的天气时必须调用此工具！",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "要查询的城市名称！例如：北京、上海、广州！"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式！当用户需要算数时必须调用此工具！例如：1+1、25*4、10/2！",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式！例如：1+1、25*4、10/2！"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("多工具调用演示（改进版）")
    print("=" * 50)
    
    # 1. 创建客户端
    client = OpenAI(
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 2. 用户提问！（一次问两个问题！）
    user_question = "北京天气怎么样？顺便算一下25乘以4等于多少？"
    print(f"用户提问：{user_question}")
    print()
    
    # 3. 消息列表！
    messages = [
        {"role": "system", "content": "你是一个助手！你有两个工具：get_weather查天气、calculate算数！当用户问天气时必须调用get_weather！当用户需要算数时必须调用calculate！"},
        {"role": "user", "content": user_question}
    ]
    
    # 4. 循环！直到大模型不再调用工具！
    print("【工具调用循环开始】")
    round_count = 0
    while True:
        round_count += 1
        print(f"  第{round_count}轮调用大模型...")
        
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            tools=tools
        )
        message = response.choices[0].message
        
        # 如果大模型不再调用工具！就回答用户！结束！
        if not message.tool_calls:
            print(f"  大模型不再调用工具！最终回答：{message.content}")
            break
        
        # 大模型要调用工具！把请求加到消息里！
        messages.append(message)
        
        # 逐个执行工具！
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            if tc.function.name == "get_weather":
                result = get_weather(args["city"])
            elif tc.function.name == "calculate":
                result = calculate(args["expression"])
            else:
                result = "不知道这个工具"
            print(f"  执行{tc.function.name}({args}) → {result}")
            
            # 把工具结果加到消息里！
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })
        
        # 防止死循环！最多10轮！
        if round_count >= 10:
            print("  超过10轮！强制停止！")
            break
    
    # 5. 总结！
    print()
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 多工具调用有两种形式：并行（一次多个请求）和串行（分多轮）！")
    print("2. glm-4-flash是串行的！一轮调一个工具！")
    print("3. 所以要加循环！处理多轮工具调用！")
    print("4. 直到大模型不再调用工具！就生成最终回答！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
