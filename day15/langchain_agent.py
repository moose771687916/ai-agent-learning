# ============================================================
# day15/langchain_agent.py - 用LangChain写Agent
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# ============================================================
# 定义工具
# ============================================================

@tool
def get_weather(city: str) -> str:
    """查询某个城市的天气"""
    # 假装查天气
    return f"{city}今天晴，25度"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，比如 1+1"""
    # 假装计算
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except:
        return "计算错误"


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("用LangChain写Agent")
    print("=" * 50)
    
    # 1. 创建大模型
    llm = ChatOpenAI(
        model="glm-4-flash",
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 2. 把工具列表传进去
    tools = [get_weather, calculate]
    
    # 3. 把工具绑定到大模型上
    llm_with_tools = llm.bind_tools(tools)
    
    # 4. 提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的助手，可以调用工具帮助用户"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # 5. 把它们串起来
    chain = prompt | llm_with_tools
    
    # 5. 对话循环
    messages = []
    
    while True:
        # 让用户输入问题
        user_input = input("\n你：")
        if user_input == "退出":
            break
        
        messages.append(HumanMessage(content=user_input))
        
        # 循环处理工具调用
        while True:
            # 调用Chain
            result = chain.invoke({"messages": messages})
            
            # 如果AI不调用工具，就回答用户
            if not result.tool_calls:
                print(f"AI：{result.content}")
                messages.append(result)
                break
            
            # 如果AI要调用工具
            messages.append(result)
            
            for tool_call in result.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                print(f"[调用工具：{tool_name}，参数：{tool_args}]")
                
                # 调用工具
                if tool_name == "get_weather":
                    tool_result = get_weather.invoke(tool_args)
                elif tool_name == "calculate":
                    tool_result = calculate.invoke(tool_args)
                else:
                    tool_result = "不知道这个工具"
                
                print(f"[工具返回：{tool_result}]")
                
                # 把工具结果加到对话历史里
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
