# Day 10 - MCP入门

## 今天学了什么？

今天我们学了**MCP（Model Context Protocol）**，这是一个让大模型能调用外部工具的标准协议。

---

## 什么是MCP？

**MCP = Model Context Protocol = 模型上下文协议**

简单来说：MCP就是一个**标准化的工具接口**。

以前每个人都要自己写工具，现在大家按MCP标准写工具，谁都能用。

---

## 我们今天做了什么？

我们写了两个文件：

### 1. mcp_server.py - MCP服务器

我们自己写的MCP服务器，提供两个工具：
- `get_exchange_rate` - 查汇率
- `get_stock_index` - 查股票指数

### 2. mcp_client.py - MCP客户端

MCP客户端，连接我们自己的MCP服务器，让大模型能调用这些工具。

---

## 整个流程是什么？

```
用户问问题
    ↓
MCP客户端把问题和工具列表发给大模型
    ↓
大模型判断要不要用工具
    ↓
如果要用 → MCP客户端调用MCP服务器上的工具
    ↓
MCP服务器执行工具，返回结果
    ↓
MCP客户端把结果发给大模型
    ↓
大模型整理成回答，告诉用户
```

---

## 关键代码讲解

### mcp_server.py

```python
from mcp.server.mcpserver import MCPServer

# 创建MCP服务器
mcp = MCPServer("macro-eco-tools")

# 加工具：查汇率
@mcp.tool()
def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """查汇率，比如美元兑人民币、欧元兑美元"""
    ...

# 启动MCP服务器
if __name__ == "__main__":
    mcp.run()
```

### mcp_client.py

```python
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

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
        
        # 用大模型聊天...
```

---

## 遇到的问题和解决方法

### 问题1：mcp版本不对

**问题**：mcp 2.x版本改了API，FastMCP改名叫MCPServer了。

**解决**：用新的API：
```python
from mcp.server.mcpserver import MCPServer
```

### 问题2：找不到inputSchema

**问题**：mcp 2.x版本inputSchema改名叫input_schema了。

**解决**：
```python
"parameters": tool.input_schema
```

### 问题3：汇率API超时

**问题**：用国外的API（exchangerate-api.com）访问慢，超时了。

**解决**：换成国内的API（新浪财经）：
```python
url = f"https://hq.sinajs.cn/list=fx_s{base_currency.lower()}{target_currency.lower()}"
headers = {"Referer": "https://finance.sina.com.cn"}
```

### 问题4：No module named 'mcp'

**问题**：用户自己的Python没装mcp库。

**解决**：
```bash
python -m pip install mcp
```

---

## 学到的知识点

| 知识点 | 说明 |
|--------|------|
| MCP是什么 | 标准化的工具接口协议 |
| MCP服务器 | 提供工具的一方 |
| MCP客户端 | 连接服务器、调用工具的一方 |
| async/await | 异步编程，同时做很多事情 |
| stdio_client | 用标准输入输出通信 |
| StdioServerParameters | 怎么启动MCP服务器 |
| ClientSession | 客户端和服务器的一次会话 |
| tool_calls | 大模型要调用工具的结构化返回 |
| input_schema | 工具需要的参数格式 |

---

## MCP有什么用？

### 以前：
- 每个人都要自己写工具
- 写一次只能自己用
- 没有标准

### 现在：
- 有人写好了工具，按MCP标准发布
- 任何人只要连他的MCP服务器，就能用他的工具
- 不用自己写

---

## 就像：

| 没有MCP | 有MCP |
|---------|-------|
| 每个人都要自己做饭 | 有人开餐厅，大家去吃 |
| 每个人都要自己写查汇率工具 | 有人写了查汇率MCP服务器，大家都能用 |
| 每个人都要自己写查天气工具 | 有人写了查天气MCP服务器，大家都能用 |

---

## Day 10总结

今天我们学了MCP，这是一个非常重要的知识点：

1. ✅ 会写MCP服务器
2. ✅ 会写MCP客户端
3. ✅ 大模型能通过MCP调用工具
4. ✅ 理解了异步编程
5. ✅ 简历上能写"会MCP开发"

---

## 下一步可以做什么？

- 写更多的MCP工具（查天气、查新闻、查股票）
- 把MCP服务器部署到公网上
- 让别人也能连我们的MCP服务器
- 学习Skill（技能）
