# AI 应用开发学习日志・Day 4

> 日期：2026-09-19
> 学习主题：跨请求记忆 + 扩展工具 + 清除记忆接口
> 状态：✅ 已完成



***

## 一、今日学习目标



1. 给 Agent 加跨请求记忆（同一个 session 连续对话，AI 记得之前聊了什么）

2. 扩展更多工具

3. 加清除记忆接口



***

## 二、环境与工具



| 项目      | 内容                                |
| ------- | --------------------------------- |
| 对话 API  | 智谱 GLM（glm-4-flash）               |
| 向量化 API | 硅基流动（BAAI/bge-m3）                 |
| 项目目录    | `D:\AGENTMAKER\ai-learning\day4\` |
| 主文件     | `agent_with_memory.py`            |



***

## 三、跨请求记忆（核心）

### 1. 原理

Day 3 的 Agent 每次调 /chat 都新建 messages，AI 不记得之前聊了什么。Day 4 改成：用一个字典存每个用户的对话历史，同一个 session\_id 连续问时，把完整历史传给 AI。

### 2. 核心代码



```
\# 存所有用户的对话历史（内存字典）

sessions = {}

\# POST /chat 里的逻辑：

sid = request.session\_id

\# 新用户→建空对话；老用户→用历史

if sid not in sessions:

&#x20;   sessions\[sid] = \[{"role": "system", "content": SYSTEM\_PROMPT}]

\# 加用户新问题

sessions\[sid].append({"role": "user", "content": request.question})

\# 传完整历史给 Agent

answer = run\_agent(sessions\[sid])

\# 存 AI 回答

sessions\[sid].append({"role": "assistant", "content": answer})
```

### 3. run\_agent 函数改动



```
\# Day 3：接收问题字符串，内部新建 messages

def run\_agent(user\_question: str) -> str:

&#x20;   messages = \[...]

\# Day 4：接收外部传入的 messages（完整历史）

def run\_agent(messages: list) -> str:

&#x20;   # 直接用传进来的 messages
```

### 4. sessions vs messages



| 名字              | 是什么                                 |
| --------------- | ----------------------------------- |
| `sessions`      | 大字典，存所有用户的对话                        |
| `sessions[sid]` | 某个用户的 messages 列表                   |
| `messages`      | 对话记录流水账（system/user/assistant/tool） |



***

## 四、扩展工具

在 Day 3 的 3 个工具基础上，新增 2 个：



| 工具                       | 干什么         |
| ------------------------ | ----------- |
| get\_current\_time       | 查当前日期、时间、星期 |
| generate\_random\_number | 生成指定范围随机数   |

现在总共 **5 个工具**：天气、计算器、保养手册（RAG）、查时间、随机数。



***

## 五、清除记忆接口



```
@app.delete("/chat/{session\_id}")

def clear\_memory(session\_id: str):

&#x20;   if session\_id in sessions:

&#x20;       del sessions\[session\_id]

&#x20;       return {"message": "已清除"}
```

相当于豆包的 "+ 新对话" 按钮 —— 清空对话历史，重新开始。



***

## 六、今日核心认知



1. **记忆 = 把历史 messages 一直传下去**。不是每次新建，而是复用同一个 session 的历史。

2. **记忆存在内存里**：sessions 字典在内存中，服务器一关就没。真实产品存在数据库里（Redis/MySQL），重启不丢。

3. **AI 有记忆 ≠ AI 是计数器**：AI 记得聊了什么内容，但不会自动数 "这是第几个问题"。

4. **memory 是双向的**：user 问题和 assistant 回答都要存，缺一个都接不上话。

5. **工具想加多少加多少**：写个函数 + 加到 tools 清单 + 加到 tool\_map，就完成了。

6. **DELETE 接口**：清除某个 session 的对话历史，相当于 "新对话"。



***

## 七、Day 4 代码文件清单



| 文件                     | 说明                            |
| ---------------------- | ----------------------------- |
| `agent_with_memory.py` | 有记忆的 Agent（5 个工具 + 记忆 + 清除接口） |
| `.env`                 | 环境变量                          |



***

## 八、整体学习路线（当前进度）



| 步骤 | 内容                   | 状态              |
| -- | -------------------- | --------------- |
| ①  | 环境搭建 + 调用大模型 API     | ✅ Day 1         |
| ②  | 命令行 AI 聊天机器人         | ✅ Day 1         |
| ③  | 理解 messages 消息结构     | ✅ Day 1         |
| ④  | 结构化输出（JSON）          | ✅ Day 1         |
| ⑤  | FastAPI 接口           | ✅ Day 1         |
| ⑥  | RAG 检索增强生成           | ✅ Day 2         |
| ⑦  | Agent 智能体开发          | ✅ Day 2         |
| ⑧  | Agent 接口化 + RAG 工具整合 | ✅ Day 3         |
| ⑨  | **跨请求记忆 + 扩展工具**     | ✅ **Day 4（今天）** |

**已完成核心能力**：API 调用、多轮对话、结构化输出、FastAPI 接口、RAG 知识库、Agent 工具循环、RAG 作为工具、跨请求记忆、5 个工具、清除记忆。

**下一步可选**：记忆持久化（存数据库）、更多工具、真实天气 API、前端界面、LangChain 框架、完整项目。