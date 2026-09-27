# ============================================================
# day10/mcp_client.py - MCP客户端
# ============================================================

from mcp.client import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import asyncio
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# 大模型客户端
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

async def main():
    # 连接MCP服务器
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            # 获取MCP服务器上的工具列表
            tools = await session.list_tools()
            print("MCP服务器上的工具：")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # 用大模型聊天
            messages = []
            while True:
                user_input = input("\n你：")
                if user_input == "退出":
                    break
                
                messages.append({"role": "user", "content": user_input})
                
                # 先问大模型要不要用工具
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    tools=[{"type": "function", "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema
                    }} for tool in tools.tools]
                )
                
                ai_message = response.choices[0].message
                
                # 如果大模型要调工具
                if ai_message.tool_calls:
                    for tool_call in ai_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = eval(tool_call.function.arguments)
                        
                        print(f"[调用工具：{tool_name}]")
                        result = await session.call_tool(tool_name, tool_args)
                        print(f"[工具返回：{result.content[0].text}]")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result.content[0].text
                        })
                    
                    # 再问大模型，让它根据工具结果回答
                    response2 = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=messages
                    )
                    answer = response2.choices[0].message.content
                    messages.append({"role": "assistant", "content": answer})
                    print(f"AI：{answer}")
                else:
                    answer = ai_message.content
                    messages.append({"role": "assistant", "content": answer})
                    print(f"AI：{answer}")

if __name__ == "__main__":
    asyncio.run(main())
