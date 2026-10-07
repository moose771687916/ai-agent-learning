# 🤖 AI Agent 开发实战（从0到1！23天！5个完整项目！）

> **从零开始，24天亲手实现 AI Agent 全栈：RAG问答 → 工具调用 → 多Agent协作 → 生产部署 → 多模态 → 车载 → 作品集！**
> 全程免费模型！全部代码可运行！

---

## ⚡ 技术栈（一目了然！）

| 类别 | 用的东西 |
|------|---------|
| 🧠 大模型 | 智谱GLM-4-Flash（对话）+ GLM-4V-Flash（看图）+ SenseVoiceSmall（听声）+ CosyVoice2（说话）+ 硅基BGE-M3（向量） |
| 🔧 框架 | LangChain（RAG/Agent）+ LangGraph（多Agent）+ Function Calling + MCP |
| 🗄️ 向量数据库 | FAISS（本地文件）+ Milvus（Lite/Server/标准三件套） |
| 🚀 部署 | Docker（镜像/容器/Compose）+ FastAPI + cpolar公网穿透 |
| 💰 成本 | 全部免费模型！（全程0元！） |

---

## 🏆 核心项目（5个！面试直接聊！）

### 项目1：RAG 知识库问答助手（Day 1-2、5-7、16、19）
- 上传文档（TXT/Word/PDF）→ 切块 → 向量化 → 检索 → LLM回答
- 亲手实现6环节RAG（不依赖框架）+ LangChain版 + 高级技巧（分块/重排序/混合搜索/多查询）
- 向量库：FAISS + Milvus（Lite/Server/标准三件套！Docker部署真Milvus！）
- **技术点**：余弦相似度、BGE-M3、Milvus三件套（etcd/MinIO/standalone）

### 项目2：多功能 Agent 助手（Day 3-4、8、17）
- 天气查询（真实API！）+ 汇率查询 + 网络搜索 + 宏观经济分析
- Function Calling 深入：工具描述、多工具、**并行调用**、出错处理
- 跨请求记忆 + JSON持久化 + 聊天前端页面
- **技术点**：function calling、工具规划、并行/串行、幻觉处理

### 项目3：多Agent协作系统（Day 18）
- LangGraph：节点/边/状态机（基础）、条件路由、**主从模式**、**人在回路（人工审核）**、循环、并行
- 主管Agent自动分配任务给多个子Agent（研究/写作/编辑）
- **技术点**：LangGraph状态管理、条件边、multi-agent架构

### 项目4：生产部署（Day 9-10、20）
- Docker打包Agent（Dockerfile + 镜像 + 容器）+ Docker Compose多容器编排
- Milvus标准三件套部署（etcd记账/MinIO存储/standalone服务）
- MCP服务器（自己写 + 连接别人的 + 多服务器 + Playwright）
- **技术点**：Docker、Compose、Milvus集群架构、MCP协议

### 项目5：多模态 + 车载Agent（Day 22-23、车企方向！）
- 看图（视觉模型！切patch原理！）+ 听声（ASR）+ 说话（TTS）+ 多模态RAG（图生文检索！）
- 完整语音Agent（听→想→说闭环！语音助手原理！）
- **车载Agent**：车载语音助手（听→想→调工具→说！"打开空调26度"真执行！）+ 车载手册RAG（FAISS持久化！离线可用！）
- **技术点**：视觉编码器、ASR/TTS、多模态RAG、车载挑战（网络差/屏幕小/安全）

---

## 📚 学习路线（23天！每天一个主题！全部跑通！）

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
| Day 21 | 评测Agent效果（LLM裁判、工具调用准确率、RAG命中率、企业评测流程） |
| Day 22 | 多模态Agent（看图glm-4v、听声ASR、说话TTS、语音Agent听想说、多模态RAG图生文、整合版三场景） |
| Day 23 | 车载Agent（车载手册RAG内存版+FAISS持久化版、车载语音助手听想说+车控天气工具） |
| Day 24 | 作品集优化（23天→5个核心项目、README名片化重写、技术博客-RAG全解析） |

---

## ✨ 核心能力（面试官最想看！）

- ✅ **RAG全栈**：手写6环节RAG + LangChain版 + 高级技巧（重排序/混合搜索/多查询）
- ✅ **Agent工具调用**：function calling 深入（并行/串行/出错处理）+ 真实API（天气/汇率/搜索）
- ✅ **多Agent协作**：LangGraph（主从/条件路由/人在回路/循环/并行）
- ✅ **向量数据库**：FAISS + Milvus（Lite/Server/标准三件套Docker部署）
- ✅ **多模态**：看图 + 听声 + 说话 + 多模态RAG（图生文检索）
- ✅ **车载Agent**：语音助手（听→想→调工具→说）+ 手册RAG（FAISS持久化离线可用）
- ✅ **部署**：Docker打包 + Compose编排 + 公网穿透
- ✅ **评测**：LLM裁判 + 工具调用准确率 + RAG命中率 + BFCL认知
- ✅ **全程免费模型**：智谱 + 硅基流动（0元学习！）

---

## 🚀 怎么运行？

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

### 3. 启动服务（Day 8宏观经济分析助手）
```
cd day8
python -m uvicorn macro_eco_assistant:app --reload
```
打开浏览器访问：http://127.0.0.1:8000/

---

## 📁 项目结构

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
├── day21/         # 评测Agent效果
├── day22/         # 多模态Agent（看图/听声/说话/多模态RAG）
├── day23/         # 车载Agent（手册RAG持久化/语音助手+车控工具）
├── day24/         # 作品集优化
└── 学习计划.md    # 完整学习计划（Day 1~25）
```
