# ============================================================
# day12/connect_external_mcp.py - 连接别人的MCP服务器
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
# 主函数：连接别人的MCP服务器，然后聊天
# ============================================================

async def main():
    # ============================================================
    # 这里就是连接别人的MCP服务器！
    # ============================================================
    
    # 例子1：连接文件系统MCP（官方的，读写本地文件）
    # 注意：这个需要先装Node.js，然后用npx运行
    server_params = StdioServerParameters(
        command="npx",  # 用npx命令（需要Node.js）
        args=["-y", "@modelcontextprotocol/server-filesystem", "D:\\AGENTMAKER\\ai-learning"]  # 打开这个文件夹
    )
    
    # 例子2：如果要连接我们自己的MCP服务器，就是这样：
    # server_params = StdioServerParameters(
    #     command="python",
    #     args=["../day10/mcp_server.py"]
    # )
    
    print("正在连接MCP服务器...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            print("连接成功！")
            
            # 获取MCP服务器上的工具列表
            tools = await session.list_tools()
            print("\nMCP服务器上的工具：")
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
                        
                        print(f"[工具返回：{result_text[:100]}...]")  # 只显示前100个字
                        
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
