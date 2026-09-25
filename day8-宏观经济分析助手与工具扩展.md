# Day 8 - 宏观经济分析助手 + 工具扩展

## 今天学了什么

### 1. 宏观经济分析助手

把Day7的通用RAG改成专门的宏观经济助手：
- 系统提示词改成"你是专业的宏观经济分析助手"
- 工具名改成search_macro_doc
- 页面标题改成"宏观经济分析助手"

本质上和Day7一样，只是换了个人设。

---

### 2. 加了查汇率工具

```python
@tool
def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """查汇率，比如美元兑人民币、欧元兑美元"""
    import requests
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    res = requests.get(url, timeout=5)
    data = res.json()
    rate = data["rates"].get(target_currency)
    return f"1 {base_currency} = {rate} {target_currency}"
```

用的是exchangerate-api.com，免费不需要API Key。

---

### 3. 加了网络搜索工具

```python
@tool
def search_web(query: str) -> str:
    """搜索网络，获取最新新闻和信息"""
    import requests
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
    res = requests.get(url, timeout=5)
    ...
```

用的是DuckDuckGo搜索，免费但效果一般。

---

### 4. 大模型的知识截止日期

| 大模型 | 知识截止到什么时候 |
|--------|------------------|
| GPT-4 | 2023年底 |
| Claude 3 | 2024年初 |
| GLM-4 | 2024年中 |

**之后发生的事情，大模型不知道，需要调工具获取实时信息。**

---

### 5. MCP和Skill是什么？

| 技术 | 是什么 | 我们在用吗 |
|------|--------|-----------|
| Function Calling | 大模型调工具的基础能力 | ✅ 在用 |
| MCP | 模型上下文协议（Anthropic提的） | ❌ 没用到 |
| Skill | AI助手的技能 | ❌ 没用到 |

MCP是更高级的方式，需要Claude模型，以后再学。

---

## 今天做了什么

- ✅ 宏观经济分析助手（RAG + 记忆 + 前端）
- ✅ 加了查汇率工具（实时数据）
- ✅ 加了网络搜索工具（实时信息）
- ✅ 生成了3个宏观经济文档（CPI/GDP/货币政策）

---

## 现在有什么工具？

| 工具 | 干什么 |
|------|--------|
| search_macro_doc | 搜索上传的宏观经济文档 |
| get_exchange_rate | 查实时汇率 |
| search_web | 搜索网络最新信息 |

---

## 明天学什么

- 加更多工具（查股市指数、查CPI数据等）
- 学LangChain的其他组件
- 整理作品集
