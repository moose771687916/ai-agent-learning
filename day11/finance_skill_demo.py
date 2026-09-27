# ============================================================
# day11/finance_skill_demo.py - 金融分析师Skill（带MCP工具）
# ============================================================

from dotenv import load_dotenv
import os
from openai import OpenAI
import asyncio

# MCP相关
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

load_dotenv()

# 大模型客户端
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

# ============================================================
# 这就是一个Skill！
# ============================================================

# 1. 提示词：告诉AI这个技能是干什么的
FINANCE_SKILL_PROMPT = """
你是一个专业的金融分析师。

你的任务：
1. 用通俗易懂的语言解释金融概念
2. 分析宏观经济对股市的影响
3. 给出投资建议（但要提醒风险）

回答要求：
- 用大白话，不要用专业术语
- 每次回答都要提醒"投资有风险，入市需谨慎"
- 不要推荐具体股票，只讲大方向
- 如果需要查实时数据（汇率、股价），就调用工具
"""

# 2. 工具：通过MCP连接（从Day 10的mcp_server.py获取）
# （下面的chat_with_skill函数会自动从MCP服务器获取工具列表）

# 3. 知识：这个技能需要什么知识
FINANCE_KNOWLEDGE = """
金融小知识：
1. CPI = 居民消费价格指数，反映物价上涨程度
2. GDP = 国内生产总值，反映经济增长
3. 降息 = 央行降低利率，刺激经济
4. 加息 = 央行提高利率，抑制通货膨胀
5. 牛市 = 股市整体上涨
6. 熊市 = 股市整体下跌
"""


# ============================================================
# 用这个Skill聊天（带MCP工具）
# ============================================================

async def chat_with_skill(user_input: str, session: ClientSession, tools) -> str:
    """用金融Skill跟用户聊天（带MCP工具）"""
    
    # 把提示词 + 知识 都放在system里
    system_prompt = FINANCE_SKILL_PROMPT + "\n\n" + FINANCE_KNOWLEDGE
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    # 把MCP工具列表转成大模型能看懂的格式
    tools_for_llm = [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema
        }
    } for tool in tools.tools]
    
    # 先问大模型
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        tools=tools_for_llm
    )
    
    ai_message = response.choices[0].message
    
    # 如果大模型要调用工具
    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = eval(tool_call.function.arguments)
            
            print(f"[调用MCP工具：{tool_name}]")
            
            # 通过MCP调用工具
            result = await session.call_tool(tool_name, tool_args)
            result_text = result.content[0].text
            
            print(f"[工具返回：{result_text}]")
            
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text
            })
        
        # 再问大模型，让它根据工具结果回答
        response2 = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages
        )
        return response2.choices[0].message.content
    else:
        return ai_message.content


# ============================================================
# 主函数：连接MCP服务器，然后聊天
# ============================================================

async def main():
    # 连接MCP服务器（就是Day 10的mcp_server.py）
    server_params = StdioServerParameters(
        command="python",
        args=["../day10/mcp_server.py"]  # 注意路径！
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            # 获取MCP服务器上的工具列表
            tools = await session.list_tools()
            print("连接到MCP服务器，可用工具：")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("-" * 50)
            print("金融分析师Skill已启动！输入'退出'结束。")
            
            # 开始聊天
            while True:
                user_input = input("\n你：")
                if user_input == "退出":
                    break
                
                answer = await chat_with_skill(user_input, session, tools)
                print(f"\n金融分析师：{answer}")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
