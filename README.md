# AI Agent 学习项目

## 项目介绍

这是一个从零开始学习AI Agent开发的项目，20天时间从零到深入掌握AI Agent开发的核心技术。

## 技术栈

- **大模型**：智谱GLM-4-Flash（对话）+ 硅基流动BGE-M3（向量）+ BGE-Reranker（重排序）
- **框架**：LangChain（Chain、RAG、Agent）+ LangGraph（多Agent协作）+ Function Calling
- **后端**：FastAPI
- **向量数据库**：FAISS + Milvus（Lite/Server/标准三件套）
- **部署**：Docker（镜像/容器/Compose）+ cpolar内网穿透

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
| Day 9 | Git与GitHub |
| Day 10 | MCP入门（自己写MCP服务器） |
| Day 11 | Skill入门 |
| Day 12 | 连接别人的MCP服务器 |
| Day 13 | 同时连接多个MCP服务器 |
| Day 14 | 深入研究Playwright MCP（25个工具） |
| Day 15 | LangChain框架深入（Chain、RAG、Agent、完整版Agent） |
| Day 16 | RAG高级技巧（分块、重排序、混合搜索、多查询、评测） |
| Day 17 | Function Calling深入（原理、工具描述、多工具、并行、出错处理） |
| Day 18 | LangGraph多Agent协作（基础、条件边、主从、人在回路、循环、并行） |
| Day 19 | 向量数据库深入（FAISS索引对比、Milvus Lite/Server、完整6环节RAG、Docker部署真Milvus） |
| Day 20 | 部署到生产环境（Docker打包Agent、镜像/容器/Dockerfile、Compose多容器编排、Milvus标准三件套） |

## 功能

- ✅ RAG文档问答（上传TXT/Word/PDF）
- ✅ Agent工具调用（天气、汇率、搜索）
- ✅ 多用户记忆（按账号区分）
- ✅ 记忆持久化（JSON文件）
- ✅ 向量库持久化（FAISS本地存储）
- ✅ 聊天前端页面（账号切换、历史记录）
- ✅ 公网部署（cpolar）
- ✅ LangChain框架（Chain流水线、RAG、Agent）
- ✅ RAG高级技巧（分块、重排序、混合搜索、多查询、评测）
- ✅ Function Calling深入（原理、工具描述、多工具、并行、出错处理）
- ✅ LangGraph多Agent协作（条件边、主从、人在回路、循环、并行）
- ✅ 向量数据库深入（FAISS三种索引对比、Milvus Lite/Server、完整6环节RAG、Docker部署真Milvus）
- ✅ 部署到生产环境（Docker镜像/容器/Dockerfile、Compose三件套、Milvus标准部署排障）

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
├── day8/          # 宏观经济分析助手与工具扩展
├── day9/          # Git与GitHub
├── day10/         # MCP入门
├── day11/         # Skill入门
├── day12/         # 连接别人的MCP服务器
├── day13/         # 同时连接多个MCP服务器
├── day14/         # 深入研究Playwright MCP
├── day15/         # LangChain框架深入
├── day16/         # RAG高级技巧
├── day17/         # Function Calling深入
├── day18/         # LangGraph多Agent协作
├── day19/         # 向量数据库深入
├── day20/         # 部署到生产环境（Docker/Compose/三件套）
└── 学习计划.md    # 完整学习计划（Day 1~25）
```
