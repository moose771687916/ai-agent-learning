# AI 应用开发学习日志・Day 1

> 日期：2026-09-15
> 学习主题：大模型 API 调用入门 + 结构化输出
> 状态：✅ 已完成



***

## 一、今日学习目标

掌握 AI 应用开发最基础的能力：



1. 搭建 Python 开发环境，调用大模型 API

2. 理解 messages 消息结构，实现多轮对话

3. 用 Prompt 约束 AI 输出 JSON 格式，做结构化任务



***

## 二、环境与工具



| 项目        | 内容                                             |
| --------- | ---------------------------------------------- |
| 操作系统      | Windows                                        |
| 编辑器       | VS Code                                        |
| Python 版本 | 3.10+                                          |
| 核心库       | `openai`（统一调用各家大模型）、`python-dotenv`（存 API Key） |
| API 平台    | DeepSeek（兼容 OpenAI 格式，新用户送额度）                  |
| 项目目录      | `D:\ai-learning\day1`                          |



***

## 三、今日完成的代码

### 1. chat.py — 命令行 AI 聊天机器人

**功能**：在命令行里和 AI 多轮对话，输入 `quit` 退出。



```
from openai import OpenAI

client = OpenAI(

\\\&#x20;   api\\\\\\\_key="你的API Key填这里",

\\\&#x20;   base\\\\\\\_url="https://api.deepseek.com"

)

messages = \\\\\\\[

\\\&#x20;   {"role": "system", "content": "你是一个 helpful 的AI助手，用简洁的中文回答。"}

]

print("=== AI 聊天机器人（输入 quit 退出）===")

while True:

\\\&#x20;   user\\\\\\\_input = input("\n你: ")

\\\&#x20;   if user\\\\\\\_input.lower() == "quit":

\\\&#x20;       break

\\\&#x20;   messages.append({"role": "user", "content": user\\\\\\\_input})

\\\&#x20;   response = client.chat.completions.create(

\\\&#x20;       model="deepseek-chat",

\\\&#x20;       messages=messages,

\\\&#x20;       temperature=0.7

\\\&#x20;   )

\\\&#x20;   answer = response.choices\\\\\\\[0].message.content

\\\&#x20;   print(f"AI: {answer}")

\\\&#x20;   messages.append({"role": "assistant", "content": answer})
```

**核心理解**：



* 每轮对话 append 两条消息（user + assistant）

* 大模型无状态，每次调用必须传完整历史

* 消息条数公式：`总条数 = 1（system） + 轮数 × 2`



***

### 2. sentiment.py — 情感分析（结构化输出）

**功能**：输入一句话，AI 返回 JSON 格式的情感分析结果（情感倾向、置信度、关键词）。



```
from openai import OpenAI

import json

client = OpenAI(

\\\&#x20;   api\\\\\\\_key="你的API Key填这里",

\\\&#x20;   base\\\\\\\_url="https://api.deepseek.com"

)

\\\\# 核心：明确规定输出格式 + 给示例（少样本提示）

system\\\\\\\_prompt = """

你是一个情感分析助手。分析用户输入的句子，返回JSON格式结果。

必须严格按以下JSON格式输出，不要输出任何其他文字：

{

\\\&#x20; "sentiment": "positive/negative/neutral",

\\\&#x20; "confidence": 0到1之间的小数,

\\\&#x20; "keywords": \\\\\\\["关键词1", "关键词2"]

}

示例：

用户：今天天气真好，心情特别棒！

返回：{"sentiment": "positive", "confidence": 0.98, "keywords": \\\\\\\["天气好", "心情棒"]}

用户：这个产品太烂了，再也不买了。

返回：{"sentiment": "negative", "confidence": 0.95, "keywords": \\\\\\\["产品烂", "不买"]}

"""

def analyze\\\\\\\_sentiment(text):

\\\&#x20;   messages = \\\\\\\[

\\\&#x20;       {"role": "system", "content": system\\\\\\\_prompt},

\\\&#x20;       {"role": "user", "content": text}

\\\&#x20;   ]

\\\&#x20;   response = client.chat.completions.create(

\\\&#x20;       model="deepseek-chat",

\\\&#x20;       messages=messages,

\\\&#x20;       temperature=0.1  # 结构化任务调低，保证输出稳定

\\\&#x20;   )

\\\&#x20;   result\\\\\\\_text = response.choices\\\\\\\[0].message.content

\\\&#x20;   print(f"AI原始返回：{result\\\\\\\_text}")

\\\&#x20;   try:

\\\&#x20;       result = json.loads(result\\\\\\\_text)  # 字符串 → 字典

\\\&#x20;       return result

\\\&#x20;   except:

\\\&#x20;       print("AI返回的不是合法JSON，需要重试或调整prompt")

\\\&#x20;       return None

if \\\\\\\_\\\\\\\_name\\\\\\\_\\\\\\\_ == "\\\\\\\_\\\\\\\_main\\\\\\\_\\\\\\\_":

\\\&#x20;   test\\\\\\\_texts = \\\\\\\[

\\\&#x20;       "今天面试通过了，太开心了！",

\\\&#x20;       "等了半小时外卖还没到，气死我了",

\\\&#x20;       "明天周一，又要上班了"

\\\&#x20;   ]

\\\&#x20;   for text in test\\\\\\\_texts:

\\\&#x20;       print(f"\n分析句子：{text}")

\\\&#x20;       result = analyze\\\\\\\_sentiment(text)

\\\&#x20;       if result:

\\\&#x20;           print(f"情感：{result\\\\\\\['sentiment']}")

\\\&#x20;           print(f"置信度：{result\\\\\\\['confidence']}")

\\\&#x20;           print(f"关键词：{result\\\\\\\['keywords']}")
```



***

### 3. sentiment\_api.py — FastAPI 接口版（模拟版 + 真实 AI 版）

**功能**：把情感分析程序封装成 HTTP 接口（POST /analyze），别人通过网址调用。

**两个版本**（都在 `D:\AGENTMAKER\ai-learning\day1\`）：



* `sentiment_api_mock.py` — 模拟版：关键词规则假装分析，不需要 API Key，先跑通接口流程

* `sentiment_api.py` — 真实版：调用智谱 GLM 大模型（glm-4-flash 免费），Key 从 .env 读取

**模拟版核心代码（理解 "接口 = 把函数变成网址"）**：



```
from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI(title="情感分析接口（模拟版）")

class SentimentRequest(BaseModel):

\&#x20;   text: str  # 请求必须传的字段，FastAPI 自动校验

@app.post("/analyze")

def analyze(request: SentimentRequest):

\&#x20;   return {"sentiment": "positive", "confidence": 0.9, "keywords": \\\[]}
```

**真实版核心代码（换成智谱 + .env 读 Key）**：



```
from dotenv import load\\\_dotenv

import os

load\\\_dotenv()                            # 读 .env（保险箱）

api\\\_key = os.getenv("ZHIPU\\\_API\\\_KEY")     # 从环境变量取 Key

client = OpenAI(

\&#x20;   api\\\_key=api\\\_key,

\&#x20;   base\\\_url="https://open.bigmodel.cn/api/paas/v4"  # 智谱地址（兼容 OpenAI 协议）

)

@app.post("/analyze")

def analyze(request: SentimentRequest):

\&#x20;   return analyze\\\_sentiment(request.text)  # 函数内部调 GLM，返回 JSON
```

**启动服务器的命令**（在 day1 目录下）：



```
python -m uvicorn sentiment\\\_api\\\_mock:app --reload   # 模拟版

python -m uvicorn sentiment\\\_api:app --reload        # 真实版
```



* `python -m`：让 Python 去自己仓库找 uvicorn（绕开 PATH 找不到的问题）

* 浏览器打开 `http://127.0.0.1:8000/docs` 测试（FastAPI 自动生成的调试页）

* 端口默认 8000，可用 `--port 8080` 改

**接口三层响应（别人收到什么）**：



1. 状态行：`200` 成功 / `422` 格式错（FastAPI 自动拦截）

2. 响应头：`Content-Type: application/json`（框架自动填，不用管）

3. 响应体：你 `return` 的字典（真正的数据）

### 4. .env 环境变量 — Key 的保险箱

**套路**：`.env` 文件存 Key → `load_dotenv()` 读进环境 → `os.getenv()` 取出来用



```
load\\\_dotenv()

api\\\_key = os.getenv("ZHIPU\\\_API\\\_KEY")

client = OpenAI(api\\\_key=api\\\_key, ...)
```

**好处**：代码里没有真实 Key；换 Key 只改 .env 一处；代码泄露 Key 不泄露

**⚠️ 注意**：.env 文件绝不上传 GitHub / 公开平台



***

## 四、今日核心知识点

### 1. 调用大模型 API 的标准写法



```
response = client.chat.completions.create(

\\\&#x20;   model="deepseek-chat",

\\\&#x20;   messages=messages,

\\\&#x20;   temperature=0.7

)

\\\\# 取结果：response.choices\\\\\\\[0].message.content
```

**response 五层结构记忆法**：

`response`（大包裹）→ `.choices`（回答列表）→ `[0]`（第一个）→ `.message`（消息对象）→ `.content`（文字内容）

其他常用字段：



* `response.usage.total_tokens` — 本次消耗的总 token

* `response.choices[0].finish_reason` — `stop`= 正常结束，`length`= 被截断

### 2. messages 消息结构（面试必问）

外层是列表 `[]`，每个元素是字典 `{}`，固定两个键：`role` 和 `content`。

三种 role：



| role        | 作用        | 出现次数    |
| ----------- | --------- | ------- |
| `system`    | 设定人设 / 规则 | 只在开头放一次 |
| `user`      | 用户说的话     | 每轮一条    |
| `assistant` | AI 之前的回答  | 每轮一条    |

**关键规律**：



* 大模型无状态：每次调用都必须把完整历史传过去，否则 AI 失忆

* 计费按 token（不是条数）：输入输出都花钱，历史重复计费

* 上下文窗口限制：DeepSeek 128K token，超出直接报错

### 3. 结构化输出的套路



1. **system prompt 里明确规定 JSON 格式**（字段名、取值范围）

2. **给 1-2 个完整示例**（少样本提示 Few-shot，比只说规则管用）

3. **temperature 设 0.1**（降低随机性，保证输出稳定）

4. **json.loads () 转字典**，然后程序做后续业务逻辑

5. **try-except 异常处理**（AI 输出不稳定是常态，必须防崩溃）

### 4. temperature 参数



| 场景          | temperature 值 | 原因        |
| ----------- | ------------- | --------- |
| 聊天、创意写作     | 0.7           | 需要多样性、自然感 |
| 结构化输出、分类、提取 | 0.1           | 需要稳定、守规矩  |



***

## 五、今日建立的核心认知



1. **AI 应用开发套路**：用 prompt 约束 AI 输出 → 解析 JSON → 程序做后续业务逻辑。所有 RAG、Agent 都建立在这个基础上。

2. **大模型无状态**：每次调用都是全新的，靠 messages 传历史维持上下文。

3. **条数 ≠ token**：消息条数是 messages 长度；token 是文字总量，计费和超限看 token。

4. **工作环境**：本地开发 Windows/Mac 都行，服务器部署 100% Linux（后续学 WSL2、Docker）。



***

## 六、待办与注意事项

* ✅ **API Key 已配置（双平台）**：
  * 智谱 `ZHIPU_API_KEY` → 对话模型 glm-4-flash（永久免费），`sentiment_api.py` 可正常调用
  * 硅基流动 `SILICONFLOW_API_KEY` → 向量化模型 BAAI/bge-m3（永久免费），Day 2 的 `rag_demo.py` 使用
  * 两个 Key 都存在 `.env`（环境变量方式），**绝不上传 GitHub**

* 📌 **Day 1 已完成到第⑤步**（FastAPI 接口）。第⑥步 RAG、第⑦步 Agent 为 Day 2 内容，详见 `day2-RAG与Agent开发.md`



***

## 七、整体学习路线（当前进度标记）



| 步骤 | 内容 | 状态 |
|------|------|------|
| ① | 环境搭建 + 调用大模型 API | ✅ 已完成（Day 1） |
| ② | 命令行 AI 聊天机器人 | ✅ 已完成（Day 1） |
| ③ | 理解 messages 消息结构 | ✅ 已完成（Day 1） |
| ④ | 结构化输出（JSON）情感分析 | ✅ 已完成（Day 1） |
| ⑤ | FastAPI 把程序做成 Web 接口 | ✅ 已完成（Day 1） |
| ⑥ | RAG 检索增强生成 | 📌 Day 2 完成，详见 day2-RAG与Agent开发.md |
| ⑦ | Agent 智能体开发 | 📌 Day 2 完成，详见 day2-RAG与Agent开发.md |
| ⑧ | CV / 语音集成 + Docker 部署 | ⬜ 未开始 |
| ⑨ | 项目打磨 + 面试准备 | ⬜ 未开始 |

**目标岗位**：AI 应用开发工程师（车企方向）

**预计周期**：4-6 个月（每天 2-3 小时）



***


## 八、Day 2 内容

Day 2 的 RAG 检索增强生成 + Agent 智能体开发内容已移至 [day2-RAG与Agent开发.md](./day2-RAG与Agent开发.md)，包括：

- RAG 原理、双平台分工、cosine_similarity 详解、切块、JSON 溯源、rag_api 接口、RAG 局限深挖
- Agent 原理（AI+工具+循环）、tools 清单、tool_map 映射、run_agent 核心循环、两个 for 循环详解、列表推导式（后置 for 循环）、运行结果
