# Day 6 - 上传文档建RAG + 部署到公网

## 今天学了什么

### 1. 上传文档建RAG

**之前的RAG**：文档写死在代码里。
**今天的RAG**：用户自己上传文件，自动建知识库。

流程：
```
用户上传文件
    ↓
读取文件内容（TXT/Word/PDF）
    ↓
按段落切块
    ↓
每块转向量
    ↓
存进向量库
    ↓
AI就能回答文档相关问题
```

---

### 2. 文件上传接口

```python
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
```

| 部分 | 意思 |
|------|------|
| @app.post | POST接口（传数据用POST） |
| "/upload" | 接口路径 |
| UploadFile | FastAPI自带的文件接收 |
| File(...) | 文件是必须的，不能不传 |

---

### 3. 支持的文件格式

| 格式 | 怎么读 |
|------|--------|
| TXT | decode utf-8 |
| Word (.docx) | python-docx库 |
| PDF | PyPDF2库 |

**只能读文字，图片、表格、格式都读不出来。**

---

### 4. HTTP方法

| 方法 | 干什么 |
|------|--------|
| GET | 拿数据（打开网页） |
| POST | 传数据（发问题、上传文件） |
| DELETE | 删除数据（清除记忆） |

---

### 5. async/await

- `async`：定义异步函数
- `await`：等慢操作完成
- 一个async函数里可以有多个await

---

### 6. 部署到公网（cpolar）

**什么是内网穿透？**
把你电脑内网里的服务暴露到公网，让别人也能访问。

```
别人 ←→ cpolar服务器 ←→ 你电脑（内网）
```

**cpolar免费版**：
- 随机域名
- 带宽小
- 同时只能1个隧道
- 国内不用VPN

---

### 7. 记忆持久化

和Day5一样，存成sessions.json，重启还在。

---

## 今天做了什么

- ✅ 上传TXT文件建RAG
- ✅ 记忆持久化（sessions.json）
- ✅ 加Word文件支持
- ✅ 加PDF文件支持
- ✅ 部署到公网（cpolar）
- ✅ 生成requirements.txt（新电脑一键装库）

---

## 明天可以学

- 高级RAG（处理排版、表格、图片）
- 做个完整项目（汽车保养助手）
- 学LangChain的RAG组件
