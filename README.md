# AI Agent 学习项目

## 项目介绍

这是一个从零开始学习AI Agent开发的项目，8天时间从零到做出一个完整的AI应用。

## 技术栈

- **大模型**：智谱GLM-4-Flash（对话）+ 硅基流动BGE-M3（向量）
- **框架**：LangChain + LangGraph
- **后端**：FastAPI
- **向量数据库**：FAISS
- **部署**：cpolar内网穿透

## 学习内容

| Day | 内容 |
|-----|------|
| Day 1 | API调用、FastAPI入门 |
| Day 2 | RAG原理、手写余弦相似度、Agent开发 |
| Day 3 | Agent接口化、RAG做成工具 |
| Day 4 | 跨请求记忆、工具扩展 |
| Day 5 | 记忆持久化（JSON）、向量库持久化、真实天气API、聊天前端页面、LangChain入门 |
| Day 6 | 上传文档建RAG（TXT/Word/PDF）、cpolar部署公网 |
| Day 7 | LangChain RAG组件（自动切块+FAISS）、向量库持久化 |
| Day 8 | 宏观经济分析助手、工具扩展（查汇率+网络搜索） |

## 功能

- ✅ RAG文档问答（上传TXT/Word/PDF）
- ✅ Agent工具调用（天气、汇率、搜索）
- ✅ 多用户记忆（按账号区分）
- ✅ 记忆持久化（JSON文件）
- ✅ 向量库持久化（FAISS本地存储）
- ✅ 聊天前端页面（账号切换、历史记录）
- ✅ 公网部署（cpolar）

## 怎么运行？

### 1. 安装依赖

```
python -m pip install -r day6/requirements.txt
python -m pip install faiss-cpu python-docx PyPDF2
```

### 2. 配置环境变量

在每个day文件夹下创建`.env`文件：

```
ZHIPU_API_KEY=你的智谱API Key
SILICONFLOW_API_KEY=你的硅基流动API Key
QWEATHER_API_KEY=你的和风天气API Key
```

### 3. 启动服务

```
cd day8
python -m uvicorn macro_eco_assistant:app --reload
```

打开浏览器访问：http://127.0.0.1:8000/

## 项目结构

```
ai-learning/
├── day1/          # API调用与FastAPI入门
├── day2/          # RAG与Agent开发
├── day3/          # Agent接口与RAG工具整合
├── day4/          # 跨请求记忆与工具扩展
├── day5/          # 持久化记忆与LangChain入门
├── day6/          # 上传文档建RAG与部署公网
├── day7/          # LangChain RAG组件与持久化
└── day8/          # 宏观经济分析助手与工具扩展
```
