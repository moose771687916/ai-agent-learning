# ============================================================
# day17/error_handling_demo.py - 工具调用出错怎么处理
# 核心：工具报错 ≠ 程序崩溃！把错误返回给模型！让它修正！
# ============================================================

from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()

# ============================================================
# 我们的工具（好工具的标准：永远返回字符串！永远不抛异常！）
# ============================================================

def get_weather(city: str) -> str:
    """查询某个城市的天气"""
    try:
        # 只支持北京和上海！其他城市报错！
        if city in ["北京", "上海"]:
            return f"{city}今天晴，25度"
        else:
            # 不抛异常！返回错误信息！
            return f"查询失败：没有「{city}」这个城市！我只支持北京和上海！"
    except Exception as e:
        # 兜底！任何错误都转成文字！
        return f"查询失败：{e}"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        # 不抛异常！返回错误信息！
        return f"计算失败：表达式「{expression}」不合法！错误：{e}"


# ============================================================
# 工具定义
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气情况！当用户询问任何城市的天气时必须调用此工具！目前只支持北京和上海！",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "要查询的城市名称！例如：北京、上海！"
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
# 执行工具（出错也不崩溃！返回错误信息！）
# ============================================================

def execute_tool(tool_name, args):
    """执行工具！出错也不崩溃！"""
    try:
        if tool_name == "get_weather":
            return get_weather(args["city"])
        elif tool_name == "calculate":
            return calculate(args["expression"])
        else:
            return f"执行失败：不知道「{tool_name}」这个工具！"
    except Exception as e:
        # 兜底！任何错误都转成文字！
        return f"执行失败：{e}"


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("工具调用出错怎么处理")
    print("=" * 50)
    
    # 1. 创建客户端
    client = OpenAI(
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 2. 用户提问！（火星不支持！故意让它出错！）
    user_question = "火星的天气怎么样？顺便算一下2+3等于多少？"
    print(f"用户提问：{user_question}")
    print()
    
    # 3. 消息列表！
    messages = [
        {"role": "system", "content": "你是一个助手！你有两个工具：get_weather查天气（只支持北京和上海）、calculate算数！当用户问天气时必须调用get_weather！当用户需要算数时必须调用calculate！如果工具返回错误，你要根据错误信息处理！"},
        {"role": "user", "content": user_question}
    ]
    
    # 4. 工具调用循环！
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
        
        # 模型不再调用工具！生成最终回答！结束！
        if not message.tool_calls:
            print(f"  ╰ 大模型最终回答：{message.content}")
            break
        
        # 模型要调用工具！
        messages.append(message)
        
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            
            # 执行工具！（出错也不崩溃！）
            result = execute_tool(tc.function.name, args)
            
            if "失败" in result or "错误" in result:
                print(f"  ⚠ 工具执行出错：{tc.function.name}({args}) → {result}")
                print(f"    → 不崩溃！把错误信息返回给模型！")
            else:
                print(f"  ✓ 工具执行成功：{tc.function.name}({args}) → {result}")
            
            # 把结果（成功或失败！）返回给模型！
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
    print("1. 工具报错 ≠ 程序崩溃！")
    print("2. 把错误信息当普通工具结果返回给模型！")
    print("3. 模型看到错误信息！自己修正！")
    print("4. 好工具的标准：永远返回字符串！永远不抛异常！")
    print("5. 用try/except包住工具！出错转成文字！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
