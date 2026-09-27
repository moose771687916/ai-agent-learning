# Day 7 - LangChain RAG组件 + 持久化

## 今天学了什么

### 1. LangChain RAG组件

**之前（手写版）**：自己写切块、转向量、存向量库、搜索。
**今天（LangChain版）**：LangChain一行代码搞定。

| 手写版 | LangChain版 |
|--------|------------|
| 自己写切块（split("\n\n")） | RecursiveCharacterTextSplitter自动切 |
| 自己写余弦相似度 | FAISS自动算 |
| 自己写向量库字典 | FAISS自动存 |
| 自己写搜索 | similarity_search自动搜 |

---

### 2. RecursiveCharacterTextSplitter（自动切块）

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块500字
    chunk_overlap=50     # 两块重叠50字
)
chunks = text_splitter.split_text(text)
```

**和手动切块的区别**：
- 手动：按空行切，块大小不均匀
- 自动：控制大小+有重叠+智能切（先按段落，再按句子）

---

### 3. FAISS向量数据库

**FAISS = Facebook AI Similarity Search**
脸书开源的向量搜索工具，专门用来快速找最像的东西。

```python
# 自动转向量+存向量库
vector_store = FAISS.from_texts(chunks, embeddings)

# 自动搜索
docs = vector_store.similarity_search(query, k=3)
```

---

### 4. 向量库持久化

```python
# 存到本地
vector_store.save_local("faiss_index")

# 从本地加载
vector_store = FAISS.load_local("faiss_index", embeddings)
```

重启服务器，向量库还在！

---

### 5. 为什么先手写再用框架？

| 阶段 | 用什么 | 为什么 |
|------|--------|--------|
| 学习阶段 | 手写 | 理解原理 |
| 生产阶段 | LangChain | 省事、效率高 |

就像学开车——先学手动挡知道离合器是什么，以后开自动挡才知道为什么熄火。

---

## 今天做了什么

- ✅ LangChain RAG演示（自动切块+FAISS）
- ✅ 向量库持久化（faiss_index文件夹）
- ✅ 记忆持久化（sessions.json）
- ✅ 完整前端页面（账号切换+历史记录+清除记忆）
- ✅ 对比手写版和LangChain版的区别

---

## 关键概念

| 概念 | 意思 |
|------|------|
| vectorstores（加s） | LangChain的模块（文件夹） |
| vector_store（没加s） | 你自己起的变量名 |
| 点号（.） | "的"的意思，A.B就是A的B |
| BaseModel | 定义接口需要什么数据，自动检查 |
| create_react_agent | LangChain帮你封装Agent主循环 |
| FAISS | 脸书开源的向量搜索工具 |

---

## 明天学什么

- 做完整项目（宏观经济分析助手）
- 加实时数据工具（查股价、查宏观数据）
