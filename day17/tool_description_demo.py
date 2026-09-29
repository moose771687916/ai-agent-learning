# ============================================================
# day17/tool_description_demo.py - 工具描述对比演示
# 差的描述 vs 好的描述！看大模型选哪个！
# ============================================================

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("工具描述对比演示")
    print("=" * 50)
    
    # 1. 创建客户端
    client = OpenAI(
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 2. 两个工具！
    # 工具A：差的描述！
    # 工具B：好的描述！
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather_bad",
                "description": "天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市"
                        }
                    },
                    "required": ["city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather_good",
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
        }
    ]
    
    # 3. 用户提问！
    user_question = "北京天气怎么样？"
    print(f"用户提问：{user_question}")
    print()
    
    # 4. 把问题和工具定义发给大模型！
    print("【测试】把问题和两个工具定义发给大模型！")
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是一个天气助手！当用户问天气时，调用工具！"},
            {"role": "user", "content": user_question}
        ],
        tools=tools
    )
    
    message = response.choices[0].message
    print("大模型返回：")
    print(f"  content：{message.content}")
    if message.tool_calls:
        for tc in message.tool_calls:
            print(f"  调用了工具：{tc.function.name}，参数：{tc.function.arguments}")
    else:
        print("  没有调用任何工具！")
    print()
    
    # 5. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 差的描述：'天气'、'城市' → 大模型看不懂！不知道什么时候用！")
    print("2. 好的描述：'查询某个城市的天气情况！当用户询问任何城市的天气时必须调用此工具！' → 大模型一看就懂！")
    print()
    print("写好描述的3个要点：")
    print("① description：说清楚工具是干什么的！")
    print("② 参数描述：说清楚参数传什么！给例子！")
    print("③ 触发条件：说清楚什么时候必须调用！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
