# Day 19 - 向量数据库深入

## 今天学了什么？

学习向量数据库！目标：搞清楚FAISS/Milvus/Pinecone三大主流，亲手实现完整RAG（不依赖LangChain！），面试能答"RAG的向量检索环节怎么做的？用什么向量数据库？"

---

## 今天做了什么？

1. 创建了day19文件夹
2. 写了faiss_index_demo.py，FAISS三种索引对比（Flat/IVF/HNSW）
3. 安装Docker Desktop + WSL（折腾了很久！）
4. 拉取milvusdb/milvus镜像（2.19GB！走VPN代理！）
5. 写了milvus_lite_demo.py，Milvus Lite入门（手工造向量！建库+插10条+检索3条）
6. 写了milvus_rag_demo.py，真embedding检索（BGE-M3！8篇文档！）
7. 写了milvus_full_rag.py，**完整6环节RAG**（读文档→切块→embedding→存Milvus→检索→智谱生成回答！全部亲手！）
8. Docker部署真Milvus：**单容器模式**（内置etcd+本地存储！绕开etcd/MinIO镜像拉取难题！）
9. 写了server_verify.py，真Milvus Server验证（连接+建库+插入+flush+检索！）

---

## 向量数据库核心概念

### 1. 向量数据库全景（三大主流！）
- **FAISS** = Meta出的本地库！（程序内嵌！内存/文件！快但单机！）
- **Milvus** = 企业开源库！（独立数据库！Lite版本地文件/Server版服务器！）
- **Pinecone** = 云托管库！（花钱省事！不用自己部署！）
- ⚠️ Flat/IVF/HNSW是"索引类型"！不是"数据库"！别搞混！

### 2. 三种索引（faiss_index_demo）
- **Flat**：暴力全扫！100%精确！最慢！（10万条检索27.3ms）
- **IVF**：倒排文件索引！先分组再找！快15倍！（1.9ms）
- **HNSW**：层级可导航小世界图！跳着找！快345倍！（0.08ms）建索引最慢、内存最大！
- 面试选型话术：**<10万用Flat、百万级IVF、千万级HNSW！**

### 3. Milvus Lite vs 真Server（API完全一样！）
```python
# Lite版：本地文件数据库！（其实.db是个目录！）
client = MilvusClient("milvus_rag.db")
# Server版：服务器地址！
client = MilvusClient("http://localhost:19530")
# 其他API（create_collection/insert/search）完全一样！
```
- 唯一行为差异：**Server插入后要手动flush！Lite自动！**
- 设计精髓：传"文件路径"自动Lite！传"http地址"自动连Server！

### 4. 数据持久化三层（存储位置！）
- 内存变量（FAISS默认！程序一关数据没了！）
- 文件数据库（Lite！程序关了数据还在！）
- 服务器数据库（Server！谁都能连！）
- 企业必须用"数据库"：省成本（不用重新embedding）、数据可靠、跨程序共享！

### 5. 完整6环节RAG（milvus_full_rag！亲手实现！）
```
① 读文档   ← read_doc()！打开txt读全文！
② 切块     ← chunk_text()！200字一块！（防太长/太短影响检索！）
③ embedding ← BGE-M3！文字→1024维向量！（免费！）
④ 存Milvus ← create_collection + insert！（向量+原文！）
⑤ 检索     ← search！余弦相似度取最像的3块！
⑥ 生成回答 ← 智谱glm-4-flash！只根据检索到的资料回答！
```
- 实测：问"CPI太高对股市有什么影响？" → 检索CPI原文 → 智谱答"通货膨胀严重，央行可能加息，股市跌。"✅
- 这就是企业生产RAG的核心代码形态！（很多企业裸写pymilvus+硅基流动+自己写prompt！）

### 6. "最像"是怎么算出来的？（余弦相似度！）
- 每个向量=高维空间的一个"方向"！夹角越小越像！
- 余弦相似度 = cos(夹角)：0°=1（100%像！）、90°=0（无关）、180°=-1（相反）
- Milvus默认COSINE！FAISS默认L2（欧氏距离）！
- search内部：查询向量和库里每条算一遍 → 排序 → 取top3（limit）！

### 7. Docker真Milvus部署（单容器模式！官方支持！）
- **标准三件套**（企业完整形态）：etcd（元数据）+MinIO（对象存储）+Milvus（主程序）三个容器！
- **单容器模式**（我们用的！）：官方standalone_embed.sh脚本支持！
  ```
  ETCD_USE_EMBED=true        → 内置etcd！（不用拉etcd镜像！）
  COMMON_STORAGETYPE=local   → 本地磁盘！（不用拉MinIO镜像！！）
  ```
- 同一Milvus！只是"元数据+存储"形态不同！API一样！
- 三件套强在：可扩展（加节点）、高可用（多副本）、海量数据（亿级）！
- 单容器强在：简单！学习/小项目够用！

---

## 今天学到了什么关键点？

### 1. LangChain是框架！Milvus是数据库！不是替代关系！
LangChain能用Milvus当底层（langchain_milvus）！裸写pymilvus=懂每一环！
企业"向量库环节"常裸写（少一层封装！快！可控！）
（我之前说"换模型LangChain改一行、Milvus也是改一行"、"调参LangChain黑盒"——都是错的！已修正！两个都能改一行、参数都开放！）

### 2. Milvus API层全公开！内部算法黑箱不用懂！
create_collection/insert/search传什么、返回什么——全控！
内部怎么算相似度——Milvus源码的事！（不用懂！）

### 3. drop_collection是demo习惯！生产绝不删！
demo每次重跑drop+重建=保证干净！
生产：建库一次！以后只insert/search！数据宝贵！

### 4. 真Server要flush！Lite自动！
insert → flush（提交落盘！）→ load_collection（可检索！）→ search
不flush就检索不到！（数据还在内存缓冲区！）

### 5. 国内拉Docker镜像真难！VPN代理是救命稻草！
registry-mirrors（国内加速器）2025-2026基本全挂！
Docker Desktop设置界面配代理 http://127.0.0.1:17890 → 拉镜像成功！
新版Docker Desktop（containerized）不读daemon.json！只在Settings界面配置！

### 6. 换embedding模型、调参——LangChain和裸写都一样灵活！
别把LangChain说得一无是处！（它参数开放！）真正的差别是"封装层次"不是"能不能调"！

---

## 今天遇到了什么问题？

### 1. Docker Desktop报"WSL内核版本过旧"！
实为WSL未安装！解决：管理员运行 `wsl --install` + 重启电脑！

### 2. docker.io拉镜像TLS handshake timeout！
解决：Docker Desktop Settings→Resources→Proxies 配置Clash代理 http://127.0.0.1:17890！

### 3. registry-mirrors在新版Docker Desktop不生效！
C:\Users\77168\.docker\daemon.json加了没用！只有Settings→Docker Engine界面配置生效！

### 4. MinIO镜像全挂！（折腾最久！）
- Docker Hub的minio/minio → pull access denied！
- quay.io的minio → 401 UNAUTHORIZED！
- bitnami/minio → manifest not found！
- **终极解法：官方单容器模式！COMMON_STORAGETYPE=local！根本不用MinIO！**

### 5. etcd镜像也拉不下来！（quay.io TLS超时！）
**终极解法：ETCD_USE_EMBED=true！内置etcd！不用单独拉！**

### 6. 真Server检索返回空！
加flush后解决！（Server插入要手动提交！）

### 7. 中文print输出被Windows管道吞掉！
解决：重定向到文件再Read（python -u + > xxx.log）！

---

## 一句话总结

> **今天把向量数据库搞透了！FAISS三种索引（Flat暴力/IVF分组/HNSW跳图）、Milvus Lite和真Server全跑通、亲手写完整6环节RAG（读→切→embed→存→检→生成）！Docker真Milvus用官方单容器模式（内置etcd+本地存储）绕开镜像难题部署成功！LangChain管框架、Milvus管存储——不是替代是组合！**

---

## 明天学什么？

Day 20！部署到生产环境（Docker是什么、用Docker打包Agent、Docker Compose、部署到服务器、监控、日志）！
