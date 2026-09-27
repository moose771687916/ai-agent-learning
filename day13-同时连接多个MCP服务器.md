# Day 13 - 同时连接多个 MCP 服务器

## 今天学了什么？

学会了同时连接多个 MCP 服务器，让一个 AI 助手同时拥有多个工具！



***

## 最终成果

成功同时连接了 4 个 MCP 服务器：



| MCP 服务器          | 能干什么               | 工具数量 |
| ---------------- | ------------------ | ---- |
| finance（我们自己写的）  | 查汇率、查股票            | 2 个  |
| filesystem（别人写的） | 读写文件、创建目录、搜索文件     | 14 个 |
| time（别人写的）       | 查现在几点、时区转换         | 2 个  |
| playwright（别人写的） | 自动操作浏览器、打开网页、点击、输入 | 25 个 |

**总共 43 个工具！**



***

## 今天遇到的所有错误（血泪教训）

### 错误 1：手动调用\_\_aenter ()，报 "send\_raw\_request called before run ()"

**错误现象：**



```
JSONRPCDispatcher.send\_raw\_request called before run()
```

**为什么错：**

我手动调用了 stdio\_client 的\_\_aenter () 方法，但是没有正确管理它的生命周期！

**正确做法：**

必须用`async with`来用 stdio\_client 和 ClientSession！



```
async with stdio\_client(params) as (read, write):

&#x20;   async with ClientSession(read, write) as session:

&#x20;       await session.initialize()
```



***

### 错误 2：连接成功了，但是只有 0 个服务器

**错误现象：**



```
连接成功！连接了0个MCP服务器：
```

**为什么错：**

我用了 asyncio.create\_task () 创建任务，但是等 5 秒不够，服务器还没启动好！

**正确做法：**



* 把等待时间从 5 秒改成 30 秒

* 每个任务里面加 try/except，打印错误信息



***

### 错误 3：时间 MCP 包名不对，连接失败

**错误现象：**



```
连接失败 time: unhandled errors in a TaskGroup
```

**为什么错：**

我用的包名是`@modelcontextprotocol/server-time`，这个包不存在！

**正确做法：**

换了一个包名`mcp-time-server`，就成功了！



***

### 错误 4：时间 MCP 启动时打印日志，导致报错

**错误现象：**



```
Failed to parse JSONRPC message from server

Invalid JSON: ... input\_value='MCP时间服务器正在通过stdio运行'
```

**为什么错：**

那个时间 MCP 服务器启动的时候，打印了一行日志到 stdout！

但是 stdout 是用来通信的！不应该打印日志！

**正确做法：**

这个是别人写的 MCP 服务器的问题，我们没法改！但是不影响使用！

**正确的 MCP 服务器应该：**



* 日志写到 stderr（标准错误）

* stdout（标准输出）只能用来通信



***

### 错误 5：Playwright MCP 太大，30 秒没下载完

**错误现象：**

只有 3 个 MCP 成功了，没有 playwright

**为什么错：**

Playwright MCP 太大了，第一次运行要下载很多东西，30 秒不够！

**正确做法：**

多等一会儿！用户说 "下了很久然后成功了"！



***

## 关键知识点

### 1. 为什么工具名要加服务器前缀？

因为不同 MCP 服务器可能有同名的工具！

比如：



* 文件系统 MCP 有个工具叫`read_file`

* 其他 MCP 也可能有个工具叫`read_file`

所以我们把工具名改成：



* `filesystem__read_file`

* `finance__get_exchange_rate`

* `time__get_current_time`

* `playwright__browser_navigate`

这样就不会冲突了！



***

### 2. 怎么根据工具名找到对应的 MCP 服务器？



```
server\_name, \_, tool\_name = name.partition("\_\_")
```

比如：



* 工具名是`filesystem__read_file`

* 拆分后：server\_name = "filesystem"，tool\_name = "read\_file"

* 然后找到 filesystem 对应的 session，调用 read\_file 工具



***

### 3. 为什么要等待？

因为不同 MCP 服务器启动速度不一样：



| MCP 服务器                | 启动速度     |
| ---------------------- | -------- |
| finance（我们自己写的 Python） | 很快，1 秒就好 |
| filesystem（npx 运行）     | 中等，几秒钟   |
| time（npx 运行）           | 中等，几秒钟   |
| playwright（npx 运行）     | 很慢，要下载很久 |

我们不知道每个服务器什么时候启动好，所以只能等一个固定时间！



***

### 4. 为什么要保持连接？

每个 MCP 服务器连接之后，要一直保持连接，不能退出！

所以我们在每个任务里面写了：



```
while True:

&#x20;   await asyncio.sleep(3600)  # 睡1小时，保持连接
```



***

## 最终代码结构



```
\# 1. 定义要连接的MCP服务器

SERVERS = {

&#x20;   "filesystem": StdioServerParameters(...),

&#x20;   "time": StdioServerParameters(...),

&#x20;   "finance": StdioServerParameters(...),

&#x20;   "playwright": StdioServerParameters(...),

}

\# 2. 同时连接多个MCP服务器

@asynccontextmanager

async def multi\_session():

&#x20;   sessions = {}

&#x20;   tasks = \[]

&#x20;  &#x20;

&#x20;   async def \_open(name, params):

&#x20;       try:

&#x20;           async with stdio\_client(params) as (read, write):

&#x20;               async with ClientSession(read, write) as session:

&#x20;                   await session.initialize()

&#x20;                   sessions\[name] = session

&#x20;                   while True:

&#x20;                       await asyncio.sleep(3600)

&#x20;       except Exception as e:

&#x20;           print(f"连接失败 {name}: {e}")

&#x20;  &#x20;

&#x20;   # 启动所有服务器

&#x20;   for name, params in SERVERS.items():

&#x20;       task = asyncio.create\_task(\_open(name, params))

&#x20;       tasks.append(task)

&#x20;  &#x20;

&#x20;   # 等30秒，让所有服务器启动好

&#x20;   await asyncio.sleep(30)

&#x20;  &#x20;

&#x20;   yield sessions

&#x20;  &#x20;

&#x20;   # 关闭所有任务

&#x20;   for task in tasks:

&#x20;       task.cancel()

\# 3. 获取所有工具

async def list\_all\_tools(sessions):

&#x20;   tools = \[]

&#x20;   for server\_name, session in sessions.items():

&#x20;       result = await session.list\_tools()

&#x20;       for tool in result.tools:

&#x20;           tools.append({

&#x20;               "type": "function",

&#x20;               "function": {

&#x20;                   "name": f"{server\_name}\_\_{tool.name}",  # 加服务器前缀

&#x20;                   ...

&#x20;               }

&#x20;           })

&#x20;   return tools

\# 4. 调用工具

async def dispatch\_tool\_call(sessions, name, arguments):

&#x20;   server\_name, \_, tool\_name = name.partition("\_\_")

&#x20;   session = sessions\[server\_name]

&#x20;   result = await session.call\_tool(tool\_name, arguments=arguments)

&#x20;   ...
```



***

## 今天最大的收获



1. **学会了同时连接多个 MCP 服务器**

2. **知道了工具名要加服务器前缀，避免冲突**

3. **知道了 stdio\_client 和 ClientSession 必须用 async with**

4. **知道了 MCP 服务器不能往 stdout 打印日志**

5. **知道了大 MCP 服务器启动很慢，要等很久**



***

## 下一步

Day 14：写一个完整的 AI 助手，同时连接多个 MCP 服务器，能查汇率、能读写文件、能查时间、能自动操作浏览器！