# ============================================================
# day13/connect_time_mcp.py - 连接时间MCP服务器
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
# 主函数：连接时间MCP服务器，然后聊天
# ============================================================

async def main():
    # 连接官方的时间MCP服务器
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-time"]  # 官方时间MCP服务器
    )
    
    print("正在连接时间MCP服务器...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            print("连接成功！")
            
            # 获取MCP服务器上的工具列表
            tools = await session.list_tools()
            print("\n时间MCP服务器上的工具：")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("-" * 50)
            print("输入'退出'结束。")
            
            # 开始聊天
            messages = []
            while True:
                user_input = input("\n你：")
                if user_input == "退出":
                    break
                
                messages.append({"role": "user", "content": user_input})
                
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
                        
                        print(f"[调用工具：{tool_name}]")
                        
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
                    
                    # 再问大模型
                    response2 = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=messages
                    )
                    answer = response2.choices[0].message.content
                    messages.append({"role": "assistant", "content": answer})
                    print(f"\nAI：{answer}")
                else:
                    answer = ai_message.content
                    messages.append({"role": "assistant", "content": answer})
                    print(f"\nAI：{answer}")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
