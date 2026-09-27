# AI 应用开发学习日志・Day 2

> 日期：2026-09-16 ~ 2026-09-17
> 学习主题：RAG 检索增强生成 + Agent 智能体开发
> 状态：✅ 已完成



***

## 一、今日学习目标



1. 掌握 RAG（检索增强生成）—— 让 AI 学会 "先查资料再回答"

2. 掌握 Agent（智能体）—— 让 AI 学会 "自己调用工具解决问题"

3. 理解 RAG 和 Agent 的区别与联系



***

## 二、环境与工具（沿用 Day 1）



| 项目        | 内容                                           |
| --------- | -------------------------------------------- |
| 操作系统      | Windows                                      |
| Python 版本 | 3.10+                                        |
| 核心库       | `openai`、`python-dotenv`、`fastapi`、`uvicorn` |
| 对话 API    | 智谱 GLM（glm-4-flash，永久免费）                     |
| 向量化 API   | 硅基流动（BAAI/bge-m3，永久免费）                       |
| 项目目录      | `D:\AGENTMAKER\ai-learning\day2\`            |



***

## 三、第一部分：RAG 检索增强生成（第⑥步）

### 1. RAG 是什么（一句话）

> 普通 AI = 只会死记硬背的考生（只懂训练时见过的知识）
> RAG 的 AI = 考试允许翻书的考生（先查资料，再答题）

**核心心法**：RAG 全程不改模型、不重新训练 —— 只是 "回答问题前先查资料，把资料塞进 prompt"。

### 2. RAG 完整流程（两阶段）

**阶段一：建资料库（搬家，只做一次）**



```
文档 → ①切块（每块一段） → ②每块向量化（embedding） → ③存进向量库
```

**阶段二：问答（每次提问都走）**



```
问题 → ④问题向量化 → ⑤检索最像的2块（相似度） → ⑥资料拼进prompt → ⑦AI基于资料回答
```

### 3. 三个新名词（必懂）



| 名词             | 大白话                                 |
| -------------- | ----------------------------------- |
| 向量化（embedding） | 把一句话变成一串数字（1024 个），意思相近的句子数字也相近     |
| 向量库            | 存 "文字块 + 数字" 的仓库，支持按相似度快速查找         |
| 余弦相似度          | 算两个数字串 "像不像" 的公式：越接近 1 越像，越接近 0 越不像 |

**向量化的威力**：理解 "意思" 而非死抠字面。"机油多久换一次" 和 "机油更换周期是多久" 字不同但意思相近，向量靠得近 —— 这就是 RAG 能检索到语义相近文档的原因。

### 4. 为什么用双平台？（费用为 0）



| 平台   | Key（.env 里）           | 负责                  | 费用   |
| ---- | --------------------- | ------------------- | ---- |
| 智谱   | `ZHIPU_API_KEY`       | 对话回答（glm-4-flash）   | 永久免费 |
| 硅基流动 | `SILICONFLOW_API_KEY` | 向量化找资料（BAAI/bge-m3） | 永久免费 |

**踩坑记录**：智谱 embedding-3 报 429（code 1113 余额不足）——glm-4-flash 对话免费，但 embedding 需要资源包额度，新用户资源包已领完。解决：改用硅基流动的开源 BGE-M3（永久免费 + 新用户送 2000 万 token）。

### 5. rag\_demo.py 代码结构（双平台分工）



```
\# --- 向量化客户端（硅基流动）--- 负责"找资料"

embed\_client = OpenAI(api\_key=os.getenv("SILICONFLOW\_API\_KEY"),

&#x20;                    base\_url="https://api.siliconflow.cn/v1")

EMBED\_MODEL = "BAAI/bge-m3"

\# --- 对话客户端（智谱）--- 负责"写答案"

chat\_client = OpenAI(api\_key=os.getenv("ZHIPU\_API\_KEY"),

&#x20;                   base\_url="https://open.bigmodel.cn/api/paas/v4")

CHAT\_MODEL = "glm-4-flash"

\# 工具函数1：文字 → 向量（"翻译官"）

def get\_embedding(text: str):

&#x20;   response = embed\_client.embeddings.create(model=EMBED\_MODEL, input=text)

&#x20;   return response.data\[0].embedding   # 1024 个数字

\# 工具函数2：算两个向量的相似度（手写余弦相似度）

def cosine\_similarity(vec\_a, vec\_b):

&#x20;   dot = sum(x \* y for x, y in zip(vec\_a, vec\_b))

&#x20;   norm\_a = sum(x \* x for x in vec\_a) \*\* 0.5

&#x20;   norm\_b = sum(x \* x for x in vec\_b) \*\* 0.5

&#x20;   if norm\_a == 0 or norm\_b == 0:

&#x20;       return 0

&#x20;   return dot / (norm\_a \* norm\_b)

\# 阶段一：建库（5块汽车保养文档 → 向量化 → 存vector\_store）

\# 阶段二：ask\_rag(question) 检索top2 → 拼进system prompt → AI回答(JSON)
```

**get\_embedding 的 2 个调用点（关键理解）**：



1. 建库时：`get_embedding(doc)` × 5 次（把 5 块文档都翻译好存着，只做一次）

2. 提问时：`get_embedding(question)` × 1 次（把问题翻译了去比对）

### 6. cosine\_similarity（余弦相似度）详解

**作用**：算两个向量 "像不像"，返回 0\~1 之间的数。

**公式拆解**：



* `dot`（点积）= 两个向量对应位置相乘再相加，衡量 "方向是否一致"

* `norm_a` / `norm_b`（模长）= 向量自身的长度

* 相似度 = 点积 / (模长 × 模长)

**直觉理解**：



* 两个向量方向完全相同 → 相似度 = 1

* 两个向量方向垂直 → 相似度 = 0

* 两个向量方向相反 → 相似度 = -1

**经验阈值**：0.5 只是一个旋钮，不是定律。高于 0.5 算 "相关"，低于 0.5 算 "不相关"，具体阈值要根据实际数据调整。

**top-2 检索**：把所有文档块和问题算相似度，按相似度从高到低排序，取前 2 名。这就是 "最像的 2 块资料"。

### 7. 切块（Chunking）是什么？

**为什么要切块？**



* 整篇文档太长，不能全部塞进 prompt（有 token 限制）

* 切块后只检索最相关的几块，精准、省钱

**怎么切块？**



* 按段落切（我们的 demo 就是手工切成 5 块）

* 按固定字数切（比如每 500 字一块）

* 按语义切（复杂项目用）

**切块大小的权衡**：



* 块太小：上下文不够，AI 理解不完整

* 块太大：不精准，浪费 token

### 8. JSON 溯源升级（企业版 vs 玩具版）

prompt 里要求 AI 严格按 JSON 输出：



```
system\_prompt = f"""

请严格按照 JSON 格式输出，不要输出任何其他文字：

{{"answer": "你的回答", "sources": \["依据的资料原文1", "依据的资料原文2"]}}

【资料】

{context}

"""
```

程序用 `json.loads(content)` 解析 → 得到 `{"answer": ..., "sources": [...]}`

**测试结果（3 个问题全通过）**：



| 问题               | AI 回答         | 来源          |
| ---------------- | ------------- | ----------- |
| 机油多久换一次？         | 5000 公里或 6 个月 | ✅ 机油文档原文    |
| 刹车片什么时候换？        | 厚度小于 3 毫米时    | ✅ 刹车片文档原文   |
| 正时皮带什么时候换？（库里没有） | 资料中没有相关内容     | ✅ 空列表（没瞎编！） |

**核心价值**：AI 说的每句话都有出处 → 可溯源、可信任 → 才能进企业。

### 9. rag\_api.py — 把 RAG 包成 FastAPI 接口

**结构**：



* 启动时建库一次（vector\_store）

* `POST /ask`：收 question → 返回 `{answer, sources}`

* `GET /`：打招呼

**启动命令**（在 day2 目录下）：



```
python -m uvicorn rag\_api:app --reload
```

浏览器打开 `http://127.0.0.1:8000/docs` 测试。

### 10. RAG 的局限与深挖（实测发现）

**问题 1：检索截断导致漏答**



* 问 "行驶 4 万公里要做什么保养？"→ AI 只答刹车片

* 诊断：top2 = 空调滤芯 0.574、刹车片 0.566，机油 0.562 排第 3 被 top-2 截断丢弃

* 结论：AI 没说机油 = 机油资料没送到 AI 面前

**问题 2：检索给全 ≠ 生成用全**



* 空调滤芯排第 1 进了 top2，但 AI 没用

* 结论：AI 生成是概率性的，会自行取舍

**问题 3：无阈值拦截，AI 自由发挥**



* 问 "你还好吗"→ AI 答 "作为 AI 我没有情感…"

* 根源：当前代码无相似度阈值，判断权全在 AI 手里

**问题 4：RAG 是不是让 AI 降智了？**



* 不是降智，是 prompt 规则 "只根据资料回答" 把 AI 的嘴锁住了

* 严格版宁可漏答绝不瞎编，是准确性优先的取舍

* 知识库不够大不是 AI 不够聪明

**问题 5：加一层向量是好是坏？**



* AI 内部向量（Transformer 隐层，思考过程，不可控）

* RAG 外部向量（资料索引，可控可查）

* 完全不同，RAG 是补 AI 不知道的资料，不是重复

### 11. RAG 部分核心认知



1. **RAG = 普通 AI 调用 + 一个 "检索" 步骤**。情感分析（直接问→答）不是 RAG；RAG 多的是 "查资料"（R = Retrieval 检索）。

2. **JSON 结构化输出是通用技能**：情感分析用它，RAG 用它，以后 Agent 也用。不是 RAG 专属。

3. **双平台协作是真实项目常态**：一个系统用两家免费 API 拼出完整能力。

4. **检索给全 ≠ 生成用全**：AI 生成是概率性的，会自行取舍。

5. **RAG 不是降智，是把 AI 的嘴锁住**：严格版宁可漏答绝不瞎编。



***

## 四、第二部分：Agent 智能体开发（第⑦步）

### 1. Agent 是什么（一句话）

> 普通 AI = 只会动嘴的顾问（你问什么它答什么，不会自己做事）
> Agent = 会动手的助理（AI + 工具 + 循环，自己决定调什么工具，反复尝试直到解决问题）

**公式**：`Agent = AI（大脑） + 工具（手） + 循环（反复尝试）`

### 2. Agent 和 RAG 的区别



|        | RAG             | Agent           |
| ------ | --------------- | --------------- |
| 核心能力   | 查资料             | 调工具             |
| 循环     | 没有（一次检索 + 一次回答） | 有（反复 "看结果→做决定"） |
| AI 的角色 | 回答者             | 决策者（决定调什么工具）    |
| 典型场景   | 知识库问答           | 自动化任务、多步骤推理     |

**联系**：RAG 可以是 Agent 的一个工具（Agent 决定 "我需要查资料" 时调用 RAG）。

### 3. Agent 的核心循环（ReAct 模式）



```
用户提问

&#x20; ↓

┌─────────────────────────────┐

│  ① 思考（Thought）           │

│     AI 看历史，决定下一步做什么  │

│  ② 行动（Action）            │

│     调用某个工具               │

│  ③ 观察（Observation）        │

│     拿到工具返回的结果          │

└─────────────────────────────┘

&#x20; ↓ 重复①②③，直到 AI 说"我有答案了"

&#x20; ↓

最终回答
```

### 4. agent\_demo.py 代码结构（6 大块）



```
① 导入库 + 初始化客户端

② 定义工具函数（get\_weather + calculator）

③ 工具清单 tools（给 AI 看的菜单）

④ 工具映射 tool\_map（菜名→函数的映射）

⑤ run\_agent 核心函数（★ 灵魂）

&#x20;  \- 初始化 messages

&#x20;  \- for 循环（最多5轮）

&#x20;    \- 问 AI（带 tools 菜单）

&#x20;    \- if AI 要工具：

&#x20;      \- 第一个 for 循环：把"要工具"消息加进 messages

&#x20;      \- 第二个 for 循环：执行工具 + 把结果加进 messages

&#x20;      \- 继续下一轮

&#x20;    \- else AI 给答案：

&#x20;      \- 打印，return，结束

⑥ 启动入口
```

### 5. 工具函数（第②块）

**get\_weather(city)**：查天气，用字典模拟数据库，`.get(city, 默认值)` 安全取值。

**calculator(expression)**：算数，用 `eval(expression)` 把字符串当成算式计算。教学用，真实项目需安全解析。

### 6. 工具清单 tools（第③块）—— 给 AI 看的菜单



```
tools = \[

&#x20;   {

&#x20;       "type": "function",

&#x20;       "function": {

&#x20;           "name": "get\_weather",

&#x20;           "description": "查询指定城市明天的天气",

&#x20;           "parameters": {

&#x20;               "type": "object",

&#x20;               "properties": {"city": {"type": "string", "description": "城市名"}},

&#x20;               "required": \["city"]

&#x20;           }

&#x20;       }

&#x20;   },

&#x20;   ...

]
```

**关键点**：



* `name` 必须和函数名一模一样

* `description` 是 AI 判断 "要不要用这个工具" 的依据，写得越清楚越准

* `required` 是必填参数，AI 看了会传，漏传会报错

* 工具名 / 参数名必须英文（API 规范），但参数值可以是中文

### 7. tool\_map（第④块）—— 菜名→厨师的映射



```
tool\_map = {

&#x20;   "get\_weather": get\_weather,

&#x20;   "calculator": calculator,

}
```

AI 说的工具名是字符串（如 `"get_weather"`），Python 执行需要函数对象。`tool_map` 就是把字符串翻译成函数对象的字典。

### 8. run\_agent 核心循环详解（第⑤块）

#### 8.1 初始化 messages



```
messages = \[

&#x20;   {"role": "system", "content": "你是智能助手，可以用工具..."},

&#x20;   {"role": "user", "content": user\_question}

]
```

一开始 2 条消息，后面每轮加新消息。

#### 8.2 for 循环（最多 5 轮）



```
max\_rounds = 5

for round\_num in range(max\_rounds):

&#x20;   ...
```

安全锁，防止 AI 犯糊涂死循环烧额度。AI 提前给答案会 `return` 跳出。

#### 8.3 问 AI（带 tools 菜单）



```
response = client.chat.completions.create(

&#x20;   model=MODEL,

&#x20;   messages=messages,

&#x20;   tools=tools,          # ★ 必须传，否则 AI 不知道有工具

&#x20;   temperature=0.1

)

message = response.choices\[0].message
```

`message.tool_calls` 有值 = AI 要调工具；`message.tool_calls` 是 None = AI 直接给答案。

#### 8.4 第一个 for 循环：把 "要工具" 消息加进 messages

**作用**：把 API 返回的工具调用对象，翻译成纯字典，放进 assistant 消息，append 进 messages。

**为什么需要？**



* `message.tool_calls` 里的元素是 API 返回的对象，不是字典

* `messages` 只能装纯字典（下一轮要发给 API）

* 不加这条消息，下一轮 AI 会失忆（忘了自己上一轮说过要调工具）

**展开版（普通 for 循环）**：



```
tool\_calls\_list = \[]

for tc in message.tool\_calls:

&#x20;   one\_dict = {

&#x20;       "id": tc.id,

&#x20;       "type": "function",

&#x20;       "function": {

&#x20;           "name": tc.function.name,

&#x20;           "arguments": tc.function.arguments

&#x20;       }

&#x20;   }

&#x20;   tool\_calls\_list.append(one\_dict)

messages.append({

&#x20;   "role": "assistant",

&#x20;   "content": message.content,

&#x20;   "tool\_calls": tool\_calls\_list

})
```

**简写版（列表推导式 = 后置 for 循环）**：



```
messages.append({

&#x20;   "role": message.role,

&#x20;   "content": message.content,

&#x20;   "tool\_calls": \[

&#x20;       {

&#x20;           "id": tc.id,

&#x20;           "type": "function",

&#x20;           "function": {

&#x20;               "name": tc.function.name,

&#x20;               "arguments": tc.function.arguments

&#x20;           }

&#x20;       }

&#x20;       for tc in message.tool\_calls    # ← 后置的 for 循环

&#x20;   ]

})
```

**列表推导式 = 把 "建空列表 + for 循环 + append" 压缩成一行**，for 循环写在模板后面，所以叫 "后置循环"。两者输出完全一样。

**messages 条数变化**：2 条 → 3 条（加了 assistant 消息）

#### 8.5 第二个 for 循环：执行工具 + 把结果加进 messages



```
for tc in message.tool\_calls:

&#x20;   func\_name = tc.function.name                   # 工具名，如 "get\_weather"

&#x20;   func\_args = json.loads(tc.function.arguments) # 参数从JSON字符串转成字典

&#x20;   func = tool\_map\[func\_name]                     # 从映射表找到真正的函数

&#x20;   result = func(\*\*func\_args)                     # 执行函数！\*\*把字典拆成参数

&#x20;   messages.append({

&#x20;       "role": "tool",

&#x20;       "tool\_call\_id": tc.id,                     # 必须和上面 AI 要调的工具 id 对应

&#x20;       "content": str(result)                      # 工具返回的结果（转字符串保险）

&#x20;   })
```

**关键点**：



* `json.loads()` 把参数从 JSON 字符串转成字典（因为 API 返回的 arguments 是字符串）

* `**func_args` 把字典 `{"city": "上海"}` 拆成 `city="上海"` 传进函数

* `role="tool"` 的消息必须带 `tool_call_id`，这样 AI 下一轮才知道 "这个结果对应哪个工具调用"

* `str(result)` 是保险，不管工具返回什么类型都转成字符串（API 要求 content 必须是字符串）

**messages 条数变化**：3 条 → 4 条（加了 tool 结果消息）

#### 8.6 else 分支：AI 直接给答案



```
else:

&#x20;   print(f"\n✅ AI 最终回答：{message.content}")

&#x20;   return message.content    # return 跳出函数，循环结束
```

AI 说 "我不要工具了，直接回答"→ 打印答案 → return 结束。

### 9. tool\_calls 的格式（OpenAI API 标准）



```
message.tool\_calls = \[

&#x20;   {

&#x20;       "id": "call\_abc123",

&#x20;       "type": "function",

&#x20;       "function": {

&#x20;           "name": "get\_weather",

&#x20;           "arguments": "{\\"city\\": \\"上海\\"}"

&#x20;       }

&#x20;   }

]
```

这是 OpenAI API 规定的标准格式，智谱、DeepSeek、硅基流动等兼容 OpenAI 格式的平台都这样。不确定时直接 `print(message.tool_calls)` 就能看到。

### 10. 运行结果（3 轮循环）



```
👤 你问：上海明天几度？这个温度换算成华氏度是多少？

🔄 第 1 轮

🤖 AI 决定调用工具：get\_weather({"city": "上海"})

🔧 工具执行结果：明天 32°C，晴

🔄 第 2 轮

🤖 AI 决定调用工具：calculator({"expression": "32.0\*1.8"})

🔧 工具执行结果：32.0\*1.8 = 57.6

🔄 第 3 轮

✅ 最终回答：明天上海的气温为32°C，换算成华氏度为57.6°F。
```

> 小细节：AI 第 2 轮只算了 
>
> `32.0*1.8`
>
>  没加 32，华氏度算错了（正确应该是 
>
> `32*1.8+32=89.6`
>
> ）。AI 也会犯这种小错，但不影响 Agent 流程的理解。

### 11. 每轮 messages 条数变化



| 轮次    | AI 做了什么        | messages 条数变化                    |
| ----- | -------------- | -------------------------------- |
| 初始    | —              | 2 条（system + user）               |
| 第 1 轮 | 调 get\_weather | 2→3（加 assistant 消息）→4（加 tool 结果） |
| 第 2 轮 | 调 calculator   | 4→5（加 assistant 消息）→6（加 tool 结果） |
| 第 3 轮 | 直接给答案          | 结束，return 跳出循环                   |

### 12. Agent 部分核心认知



1. **Agent = AI + 工具 + 循环**。普通 AI 只动嘴，Agent 会动手。

2. **tools = 菜单**，给 AI 看的，告诉它有什么工具可用。`description` 是 AI 判断依据。

3. **tool\_map = 菜名→厨师的映射**，AI 说字符串名，程序靠这个找到真正函数。

4. **循环 = 反复 "看结果→做决定"**。AI 每轮看历史，决定下一步调什么工具，直到给答案。

5. **第一个 for 循环 = 翻译官**，把 API 返回的对象翻译成纯字典，放进 messages。

6. **第二个 for 循环 = 真正干活**，执行工具，把结果加进 messages。

7. **列表推导式 = 后置的 for 循环**，把 "建空列表 + for+append" 压缩成一行。

8. **role=tool 的消息必须带 tool\_call\_id**，AI 下一轮才知道结果对应哪个工具。

9. **max\_rounds 是安全锁**，防止死循环烧额度。



***

## 五、整体学习路线（当前进度标记）



| 步骤 | 内容                    | 状态           |
| -- | --------------------- | ------------ |
| ①  | 环境搭建 + 调用大模型 API      | ✅ 已完成（Day 1） |
| ②  | 命令行 AI 聊天机器人          | ✅ 已完成（Day 1） |
| ③  | 理解 messages 消息结构      | ✅ 已完成（Day 1） |
| ④  | 结构化输出（JSON）情感分析       | ✅ 已完成（Day 1） |
| ⑤  | FastAPI 把程序做成 Web 接口  | ✅ 已完成（Day 1） |
| ⑥  | RAG 检索增强生成            | ✅ 已完成（Day 2） |
| ⑦  | Agent 智能体开发           | ✅ 已完成（Day 2） |
| ⑧  | CV / 语音集成 + Docker 部署 | ⬜ 未开始        |
| ⑨  | 项目打磨 + 面试准备           | ⬜ 未开始        |

**目标岗位**：AI 应用开发工程师（车企方向）

**已完成核心能力**：API 调用、多轮对话、结构化输出、FastAPI 接口、RAG 知识库问答、Agent 工具调用循环。



***

## 六、Day 2 代码文件清单



| 文件                     | 说明                                                        |
| ---------------------- | --------------------------------------------------------- |
| `rag_demo.py`          | 命令行版 RAG，双平台 + JSON 溯源，已跑通                                |
| `rag_api.py`           | 接口版 RAG，FastAPI + POST /ask，已在 /docs 实测通过                 |
| `agent_demo.py`        | Agent 主文件（双工具 + 循环 + 列表推导式），已运行验证通过                       |
| `agent_demo_simple-test.py` | 完全展开版 Agent（无列表推导式，每步加 print），用于教学                        |
| `show_messages-test.py`     | 独立演示脚本，展示 append 前后 messages 完整 JSON                      |
| `demo_for_append-test.py`   | 纯模拟脚本，展示 for 循环和 append 的关系（不调用 API）                      |
| `.env`                 | 环境变量（ZHIPU\_API\_KEY + SILICONFLOW\_API\_KEY），绝不上传 GitHub |