# ============================================================
# day13/multi_mcp_client.py - 同时连接多个MCP服务器
# ============================================================

from dotenv import load_dotenv
import os
from openai import OpenAI
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

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
# 定义要连接的MCP服务器
# ============================================================

SERVERS = {
    # 1. 文件系统MCP（读写文件）
    "filesystem": StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "D:\\AGENTMAKER\\ai-learning"]
    ),
    # 2. 时间MCP（查时间）
    "time": StdioServerParameters(
        command="npx",
        args=["-y", "mcp-time-server"]
    ),
    # 3. 我们自己的金融MCP（查汇率）
    "finance": StdioServerParameters(
        command="python",
        args=["../day10/mcp_server.py"]
    ),
    # 4. Playwright MCP（自动操作浏览器）
    "playwright": StdioServerParameters(
        command="npx",
        args=["-y", "@playwright/mcp@latest"]
    ),
}


# ============================================================
# 同时连接多个MCP服务器
# ============================================================

@asynccontextmanager
async def multi_session() -> AsyncIterator[dict[str, ClientSession]]:
    """同时打开多个MCP服务器，返回sessions字典"""
    sessions: dict[str, ClientSession] = {}
    tasks = []

    async def _open(name: str, params: StdioServerParameters) -> None:
        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:  # 用async with！
                    await session.initialize()
                    sessions[name] = session
                    print(f"  连接成功：{name}")
                    # 一直保持连接
                    while True:
                        await asyncio.sleep(3600)  # 睡1小时，保持连接
        except Exception as e:
            print(f"  连接失败 {name}: {e}")

    # 启动所有服务器任务
    for name, params in SERVERS.items():
        task = asyncio.create_task(_open(name, params))
        tasks.append(task)

    # 等一下，让所有服务器都启动好
    print("正在等待所有MCP服务器启动...（可能要几分钟）")
    await asyncio.sleep(30)  # 等30秒，让大的MCP服务器有时间下载

    try:
        yield sessions
    finally:
        for task in tasks:
            task.cancel()


# ============================================================
# 获取所有MCP的工具
# ============================================================

async def list_all_tools(sessions: dict[str, ClientSession]) -> list[dict]:
    """获取所有MCP服务器的工具，工具名加上服务器前缀"""
    tools: list[dict] = []
    for server_name, session in sessions.items():
        result = await session.list_tools()
        for tool in result.tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": f"{server_name}__{tool.name}",
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                }
            })
    return tools


# ============================================================
# 调用工具
# ============================================================

async def dispatch_tool_call(
    sessions: dict[str, ClientSession], name: str, arguments: dict
) -> str:
    """根据工具名（带服务器前缀），找到对应的MCP服务器，调用工具"""
    server_name, _, tool_name = name.partition("__")
    session = sessions[server_name]
    result = await session.call_tool(tool_name, arguments=arguments)
    # 把结果转成文本
    parts = []
    for block in result.content:
        text = getattr(block, "text", None)
        if text is not None:
            parts.append(text)
    return "\n".join(parts) if parts else "(没有输出)"


# ============================================================
# 主函数：聊天
# ============================================================

async def main():
    print("正在连接多个MCP服务器...")
    
    async with multi_session() as sessions:
        print(f"\n连接成功！连接了{len(sessions)}个MCP服务器：")
        for name in sessions.keys():
            print(f"  - {name}")
        
        tools = await list_all_tools(sessions)
        print(f"\n总共有{len(tools)}个工具：")
        for tool in tools:
            print(f"  - {tool['function']['name']}")
        
        print("-" * 50)
        print("输入'退出'结束。")
        
        messages = []
        while True:
            user_input = input("\n你：")
            if user_input == "退出":
                break
            
            messages.append({"role": "user", "content": user_input})
            
            # 先问大模型
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=messages,
                tools=tools
            )
            
            ai_message = response.choices[0].message
            
            # 如果大模型要调用工具
            if ai_message.tool_calls:
                for tool_call in ai_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = eval(tool_call.function.arguments)
                    
                    print(f"[调用工具：{tool_name}]")
                    
                    # 调用工具
                    result_text = await dispatch_tool_call(sessions, tool_name, tool_args)
                    
                    print(f"[工具返回：{result_text[:100]}...]")
                    
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
