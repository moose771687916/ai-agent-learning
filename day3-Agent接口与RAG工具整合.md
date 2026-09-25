# AI 应用开发学习日志・Day 3

> 日期：2026-09-18 ~ 2026-09-19
> 学习主题：Agent 包成 FastAPI 接口 + RAG 作为 Agent 工具
> 状态：✅ 已完成



***

## 一、今日学习目标



1. 把 Day 2 的命令行 Agent 包成 FastAPI 接口（方向 A）

2. 把 RAG（汽车保养手册）做成 Agent 的第三个工具（方向 B）

3. 深入理解 Function Calling 原理：AI 怎么判断要不要调工具



***

## 二、环境与工具（沿用）



| 项目      | 内容                                           |
| ------- | -------------------------------------------- |
| 对话 API  | 智谱 GLM（glm-4-flash，永久免费，支持 function calling） |
| 向量化 API | 硅基流动（BAAI/bge-m3，永久免费）                       |
| Web 框架  | FastAPI + Uvicorn                            |
| 项目目录    | `D:\AGENTMAKER\ai-learning\day3\`            |



***

## 三、第一部分：Agent 包成 FastAPI 接口（方向 A）

### 1. 和命令行版的区别



|      | 命令行版（agent\_demo.py）   | 接口版（agent\_api.py）                         |
| ---- | ---------------------- | ------------------------------------------ |
| 怎么用  | 跑脚本，直接 print           | 发 HTTP 请求，返回 JSON                          |
| 谁能调  | 只有你自己在终端               | 任何人 / 任何前端都能调                              |
| 启动方式 | `python agent_demo.py` | `python -m uvicorn agent_api:app --reload` |
| 核心逻辑 | 一样                     | 一样                                         |

**本质**：外面套一层 FastAPI 外壳，把函数变成网址。

### 2. 关键代码结构



```
from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI(title="智能助手 Agent 接口")

class AgentRequest(BaseModel):

&#x20;   question: str   # 请求必须传的字段

@app.post("/chat")

def chat(request: AgentRequest):

&#x20;   answer = run\_agent(request.question)

&#x20;   return {"question": request.question, "answer": answer}

@app.get("/")

def home():

&#x20;   return {"message": "接口已启动"}
```

### 3. 启动与测试



```
cd D:\AGENTMAKER\ai-learning\day3

python -m uvicorn agent\_api:app --reload

浏览器打开 http://127.0.0.1:8000/docs
```

**踩坑**：接口版不能直接 `python agent_api.py` 运行（没有启动代码），必须用 uvicorn 启动。



***

## 四、第二部分：RAG 作为 Agent 的第三个工具（方向 B）

### 1. 为什么要把 RAG 做成工具？



|                    | 用户需要自己说   | 混合问题        | 真实场景        |
| ------------------ | --------- | ----------- | ----------- |
| 单独 RAG             | 必须说 "查保养" | 答不了天气       | 不现实         |
| 单独 Agent           | 必须说 "查天气" | 答不了保养       | 不现实         |
| **Agent + RAG 工具** | **随便问**   | **AI 自己判断** | **真实用户的用法** |

**核心价值**：一个入口，AI 自己判断该用什么工具。真实用户不会说 "请调用 RAG 工具"，他只会说 "我 4 万公里了要做啥保养"。

### 2. RAG 工具的设计思路

RAG 工具**只做检索，不做回答**：



* 接收 query（用户的问题 / 关键词）

* 检索最相关的 2 块文档

* 返回文档文本给 AI

* Agent 的 AI 大脑自己综合回答

**为什么不让 RAG 工具自己调 AI 回答？** 因为 Agent 的 AI 大脑已经在那里了，不需要重复调一次 AI。工具只负责 "找资料"，AI 大脑负责 "综合回答"。

### 3. 三个工具清单



| 工具名                         | 干什么          | 参数         |
| --------------------------- | ------------ | ---------- |
| get\_weather                | 查天气          | city       |
| calculator                  | 算数           | expression |
| search\_maintenance\_manual | 查汽车保养手册（RAG） | query      |

### 4. RAG 工具核心代码



```
\# 建库（启动时建一次）

documents = \[

&#x20;   "机油...每行驶5000公里或6个月更换...",

&#x20;   "轮胎胎压...每月检查...",

&#x20;   "刹车片...厚度小于3毫米时必须更换...",

&#x20;   "空调滤芯...每1万公里或一年更换...",

&#x20;   "电瓶...寿命一般在2到4年...",

]

vector\_store = \[]

for doc in documents:

&#x20;   vector\_store.append({"text": doc, "vector": get\_embedding(doc)})

\# RAG 工具函数

def search\_maintenance\_manual(query: str) -> str:

&#x20;   query\_vector = get\_embedding(query)

&#x20;   scored = \[(cosine\_similarity(query\_vector, item\["vector"]), item\["text"])

&#x20;             for item in vector\_store]

&#x20;   scored.sort(reverse=True)

&#x20;   top2 = scored\[:2]

&#x20;   return "\n---\n".join(text for \_, text in top2)
```



***

## 五、Function Calling 原理详解（今日核心）

### 1. AI 怎么判断要不要调工具？—— 一句话

> AI 本身不能执行代码，只能输出文字。我们给它一张菜单（tools 清单），AI 看了用户问题 + 菜单，自己决定 "这个问题需要点哪个菜"，然后它 "说" 出来（输出 tool_calls），我们的代码听到后去真正执行。

### 2. 完整流程（5 步）



```
第1步：我们把"菜单"（tools清单）和对话历史一起传给 AI

第2步：AI 看用户问题 + 菜单，自己判断需要什么工具

第3步：AI 输出"点菜单"（tool\_calls 结构化文字）

第4步：我们的代码解析 tool\_calls，真正执行工具函数

第5步：把工具结果喂回给 AI（append 进 messages），进入下一轮
```

### 3. AI 靠什么判断？

**两个东西**：



1. **tools 清单里的 description**（最重要）—— 告诉 AI 这个工具是干嘛的，什么时候用

2. **system prompt 里的规则**—— 告诉 AI"需要工具时调用，不需要时直接回答"

### 4. 关键规则



| 问题         | 答案                                 |
| ---------- | ---------------------------------- |
| 一轮能调几个工具？  | 任意多个（遍历 message.tool\_calls 列表）    |
| 调完一轮能继续调吗？ | 能！每一轮 AI 都可以再调工具                   |
| 什么时候停？     | AI 判断 "信息够了"，直接给答案（else 分支 return） |
| 最多几轮？      | 5 轮（安全锁 max\_rounds）               |
| 会忘记之前的结果吗？ | 不会！每轮传完整 messages，只增不删             |
| 简单问题会调工具吗？ | 不会！AI 自己判断，闲聊 / 简单计算直接回答           |

### 5. 真实运行验证

用户问："我明天开车去上海，明天几度？4 万公里要做什么保养？"



```
第1轮：🤖 AI 调 get\_weather(上海) → "明天 32°C，晴"

第2轮：🤖 AI 调 search\_maintenance\_manual("4万公里保养") → 空调滤芯+刹车片资料

第3轮：✅ 最终回答："明天上海32°C，晴。4万公里需要更换空调滤芯和检查刹车片。"
```

**验证了**：



* AI 自己判断该调什么工具 ✅

* 多轮循环，每轮看结果再决定 ✅

* 最终答案综合了所有工具结果 ✅

* 没有遗忘第一轮的天气结果 ✅



***

## 六、今日核心认知



1. **Agent = AI 大脑 + 工具 + 循环**。工具想加多少加多少，RAG 只是其中一个。

2. **Function Calling 的本质**：AI 不能执行代码，只能输出文字。tools 清单是菜单，AI 看菜单决定点什么，代码听到后真正执行。

3. **description 是 AI 判断的关键**：工具描述写得越清楚，AI 判断越准。

4. **一轮可以同时调多个工具**：for 循环遍历 message.tool\_calls，每个都执行。

5. **多轮循环不会遗忘**：messages 只增不删，每轮传完整历史，AI 永远记得之前的结果。

6. **每轮 AI 二选一**：要么调工具继续循环，要么给答案 return 结束。不能 "答了一半再调工具"。

7. **RAG 作为工具 vs 独立 RAG**：独立 RAG 只能回答资料里的问题；RAG 做成 Agent 工具后，AI 自己判断什么时候该查资料，其他问题自由回答。

8. **接口版 vs 命令行版**：核心逻辑一样，只是外面套 FastAPI 外壳，把函数变成网址。



***

## 七、Day 3 代码文件清单



| 文件             | 说明                                                  |
| -------------- | --------------------------------------------------- |
| `agent_api.py` | Agent 接口版（3 个工具：天气 / 计算器 / 保养手册），FastAPI POST /chat |
| `.env`         | 环境变量（ZHIPU\_API\_KEY + SILICONFLOW\_API\_KEY）       |



***

## 八、整体学习路线（当前进度）



| 步骤 | 内容                       | 状态              |
| -- | ------------------------ | --------------- |
| ①  | 环境搭建 + 调用大模型 API         | ✅ Day 1         |
| ②  | 命令行 AI 聊天机器人             | ✅ Day 1         |
| ③  | 理解 messages 消息结构         | ✅ Day 1         |
| ④  | 结构化输出（JSON）情感分析          | ✅ Day 1         |
| ⑤  | FastAPI 把程序做成 Web 接口     | ✅ Day 1         |
| ⑥  | RAG 检索增强生成               | ✅ Day 2         |
| ⑦  | Agent 智能体开发              | ✅ Day 2         |
| ⑧  | **Agent 接口化 + RAG 工具整合** | ✅ **Day 3（今天）** |
| ⑨  | 跨请求记忆 / 更多工具 / 项目打磨      | ⬜ 明天继续          |

**已完成核心能力**：API 调用、多轮对话、结构化输出、FastAPI 接口、RAG 知识库问答、Agent 工具调用循环、RAG 作为 Agent 工具。