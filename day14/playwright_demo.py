# ============================================================
# day14/playwright_demo.py - 专门研究Playwright MCP
# ============================================================

from dotenv import load_dotenv
import os
import glob
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
# 只连接Playwright MCP
# ============================================================

@asynccontextmanager
async def playwright_session() -> AsyncIterator[ClientSession]:
    """只连接Playwright MCP"""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@playwright/mcp@latest"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("连接成功：playwright")
            yield session


# ============================================================
# 主函数：聊天
# ============================================================

async def main():
    print("正在连接Playwright MCP...")
    print("（第一次运行要下载很久，请耐心等待）")
    
    async with playwright_session() as session:
        # 获取所有工具
        result = await session.list_tools()
        tools = result.tools
        
        print(f"\nPlaywright MCP总共有{len(tools)}个工具：")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.name} - {tool.description[:50]}...")
        
        print("-" * 50)
        print("现在你可以让AI帮你自动操作浏览器了！")
        print("比如：打开百度，搜索乒乓球")
        
        # 系统提示词
        messages = [
            {
                "role": "system",
                "content": """你是一个自动操作浏览器的专家！

每次你调用完任何工具之后，系统都会自动等页面加载完，然后自动给你看页面快照！

你只需要做：
1. 打开网页（browser_navigate）
2. 从自动给你的页面快照里，找所有可以输入文字的地方（比如textbox、input、contenteditable），选择第一个，它就是搜索输入框，记住它的ref
3. 调用browser_type，在这个可以输入文字的地方里输入用户要搜索的内容
4. 调用browser_press_key，传key="Enter"，提交搜索
5. 等搜索结果加载完，自动快照会给你看搜索结果页面
6. 从搜索结果页面里整理出用户要的信息，告诉用户就可以了！

重要！
- 搜索完之后，整理结果告诉用户就可以了！
- 不要瞎点别的东西！
- 用户没让你点别的东西！

重要！用户说要搜索什么的时候：
- 你要在页面快照里找textbox（文本输入框）！
- textbox就是可以输入文字的地方！
- 用户要搜索的内容，是要输入到这个textbox里的！
- 不是在页面上找用户要搜索的那个词！

健壮性要求！
- 如果用browser_find找不到，不要卡住！换个方式！
- 直接找textbox（文本输入框），在里面输入用户要搜索的内容！
- 然后按回车键提交搜索！

绝对禁止：
- 禁止用CSS选择器！
- 禁止瞎猜元素的ref！
- 只能用系统自动给你的页面快照里看到的ref值！
"""
            }
        ]
        
        while True:
            user_input = input("\n你：")
            if user_input == "退出":
                break
            
            messages.append({"role": "user", "content": user_input})
            
            # 把工具传给大模型
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema,
                    }
                })
            
            # 先问大模型
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=messages,
                tools=openai_tools
            )
            
            # 循环处理工具调用，直到大模型不再调用工具为止！
            while True:
                ai_message = response.choices[0].message
                
                # 如果大模型不调用工具了，就退出循环
                if not ai_message.tool_calls:
                    answer = ai_message.content
                    messages.append({"role": "assistant", "content": answer})
                    print(f"\nAI：{answer}")
                    break
                
                # 如果大模型要调用工具
                for tool_call in ai_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = eval(tool_call.function.arguments)
                    
                    print(f"[调用工具：{tool_name}]")
                    print(f"[参数：{tool_args}]")
                    
                    # 调用工具
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    
                    # 把结果转成文本
                    parts = []
                    for block in result.content:
                        text = getattr(block, "text", None)
                        if text is not None:
                            parts.append(text)
                    result_text = "\n".join(parts)
                    
                    # 如果是browser_snapshot，读取快照文件的内容！
                    if tool_name == "browser_snapshot":
                        # 看看大模型传的filename参数是什么
                        filename = tool_args.get("filename", "snapshot.yml")
                        # 读取文件内容
                        try:
                            with open(filename, "r", encoding="utf-8") as f:
                                snapshot_content = f.read()
                            # 把文件内容加到结果里
                            result_text = result_text + "\n\n页面快照内容：\n" + snapshot_content
                        except:
                            # 如果读不到，就找最新的page-*.yml文件
                            snapshot_files = glob.glob(".playwright-mcp/page-*.yml")
                            if snapshot_files:
                                latest_file = max(snapshot_files, key=os.path.getctime)
                                try:
                                    with open(latest_file, "r", encoding="utf-8") as f:
                                        snapshot_content = f.read()
                                    result_text = result_text + "\n\n页面快照内容：\n" + snapshot_content
                                except:
                                    pass
                    
                    print(f"[工具返回：{result_text[:200]}...]")
                    
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
                    
                    # 强制！自动调用一次browser_snapshot！
                    # 不管大模型记不记得，我们都强制它看页面上有什么！
                    
                    # 只有调用完browser_navigate之后，才等2秒！
                    # 调用完其他工具，不用等！
                    if tool_name == "browser_navigate":
                        print("[等页面加载完...]")
                        await asyncio.sleep(2)
                    
                    print("[自动调用browser_snapshot...]")
                    auto_snapshot = await session.call_tool("browser_snapshot", arguments={})
                    auto_parts = []
                    for block in auto_snapshot.content:
                        text = getattr(block, "text", None)
                        if text is not None:
                            auto_parts.append(text)
                    auto_result_text = "\n".join(auto_parts)
                    
                    # 读取快照文件内容
                    snapshot_files = glob.glob(".playwright-mcp/page-*.yml")
                    if snapshot_files:
                        latest_file = max(snapshot_files, key=os.path.getctime)
                        try:
                            with open(latest_file, "r", encoding="utf-8") as f:
                                snapshot_content = f.read()
                            auto_result_text = auto_result_text + "\n\n页面快照内容：\n" + snapshot_content
                        except:
                            pass
                    
                    print(f"[自动快照：{auto_result_text[:200]}...]")
                    
                    # 把新的快照加到结果里
                    final_content = result_text + "\n\n" + auto_result_text
                    
                    # 把之前旧的快照都删掉！只保留最近的一个！
                    for msg in messages:
                        if msg["role"] == "tool" and "页面快照内容" in msg["content"]:
                            # 把旧的快照内容删掉，只留个提示
                            msg["content"] = msg["content"].split("\n\n页面快照内容：")[0] + "\n\n（旧的页面快照已自动清理）"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": final_content
                    })
                
                # 再问大模型
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    tools=openai_tools
                )


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
