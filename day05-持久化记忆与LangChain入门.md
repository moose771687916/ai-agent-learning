# Day 5 - 持久化记忆 + 真实天气 + 聊天前端 + LangChain 入门

## 今天学了什么

### 1. 记忆持久化

**之前的问题**：记忆存在内存字典里，重启服务器就没了。

**解决**：把 sessions 字典存成 JSON 文件



```
def load\_sessions():

&#x20;   if os.path.exists("sessions.json"):

&#x20;       return json.load(open("sessions.json", encoding="utf-8"))

&#x20;   return {}

def save\_sessions():

&#x20;   json.dump(sessions, open("sessions.json", "w", encoding="utf-8"), ensure\_ascii=False)
```

**效果**：重启服务器后 AI 还记得之前聊了什么。



***

### 2. 向量库持久化

**之前的问题**：每次启动都重新调 embedding API 建向量库（5 次调用）。

**解决**：向量库存成 JSON 文件，存在就直接读。



```
if os.path.exists("vector\_store.json"):

&#x20;   vector\_store = json.load(open("vector\_store.json", encoding="utf-8"))

else:

&#x20;   # 第一次建库，调embedding API
```

**效果**：第二次启动秒开，不重复调 API。



***

### 3. 真实天气 API（和风天气）

**之前的问题**：天气是假的，写死在代码里。

**解决**：接和风天气真实 API



* API Key：存在.env 里

* 两步查询：先查城市 ID，再查实时天气

* 免费额度：每月 5 万次

**踩坑记录**：



* 旧域名 [geoapi.qweather.com](https://geoapi.qweather.com) = 404

* [api.qweather.com](https://api.qweather.com) = 403 Invalid Host

* 正确：每个项目有专属 API Host（[p84wcwk7vm.re.qweatherapi.com](https://p84wcwk7vm.re.qweatherapi.com)）



***

### 4. 聊天前端页面

**之前的问题**：只能在 /docs 页面测试，不直观。

**做了什么**：写了个 HTML 聊天页面

功能：



* 账号输入框（可以输入自己的 ID）

* 下拉选择框（选已有的账号）

* 聊天窗口（用户蓝色，AI 灰色）

* 清除记忆按钮（带确认框）

* 切换账号自动加载历史记录



***

### 5. LangChain 框架入门

**核心概念**：



| 概念                                 | 干什么                   |
| ---------------------------------- | --------------------- |
| @tool 装饰器                          | 自动生成工具清单 JSON，不用手写    |
| create\_react\_agent(model, tools) | 一行代码代替 50 行 Agent 主循环 |
| MemorySaver                        | 帮你管 sessions 字典，不用自己写 |
| thread\_id                         | 就是 session\_id，区分不同用户 |

**代码量对比**：



|     | 手写版     | LangChain 版                              |
| --- | ------- | ---------------------------------------- |
| 总行数 | \~400 行 | \~280 行                                  |
| 省在哪 |         | 不用写工具清单 JSON、不用写 tool\_map、不用写 Agent 主循环 |

**消息格式对比**：



|        | 手写版（字典）                                 | LangChain 版（元组）   |
| ------ | --------------------------------------- | ----------------- |
| system | {"role": "system", "content": "..."}    | ("system", "...") |
| 用户     | {"role": "user", "content": "..."}      | ("human", "...")  |
| AI     | {"role": "assistant", "content": "..."} | ("ai", "...")     |



***

### 6. LangChain 记忆组件

**MemorySaver**：



* 存在内存里，重启就没了

* 学习测试用，省事

**SqliteSaver**：



* 存在 SQLite 数据库文件里，重启还在

* 生产环境用

* 学习阶段不用 —— 黑盒，学不到原理



***

## 今天做了什么



* ✅ 记忆持久化（sessions.json）

* ✅ 向量库持久化（vector\_store.json）

* ✅ 真实天气 API（和风天气）

* ✅ 聊天前端页面（账号切换 + 历史记录 + 清除记忆）

* ✅ LangChain 框架入门（对比手写版）

* ✅ LangChain 记忆组件（MemorySaver/SqliteSaver）



***

## 明天可以学



* 上传文档建 RAG（用户上传 PDF 自动建知识库）

* 部署到公网（让别人也能访问你的 AI）

* LangChain 高级功能（RAG、链、代理）