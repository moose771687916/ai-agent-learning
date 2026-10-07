# Day 20 - 部署到生产环境

## 今天学了什么？

学习部署！目标：搞懂Docker是什么、怎么用Docker打包自己的Agent、Docker Compose多容器编排、Docker排障！最终把Milvus标准三件套（etcd+MinIO+Milvus）真正搭起来，跑通完整RAG！面试能答"怎么把Agent部署上线？"

---

## 今天做了什么？

1. 创建了day20文件夹
2. 写了agent_app.py，FastAPI对话Agent（GET /健康检查 + POST /chat接收{message}返回{reply}）
3. 写了requirements.txt + Dockerfile（python:3.12-slim + 清华pip源 + uvicorn启动）
4. `docker build -t day20-agent .` 成功（271MB！）+ `docker run` 容器跑起来 + POST /chat实测中文正常！
5. 演示docker logs（看请求日志）、docker stop/start（容器生命周期）
6. **Docker拉镜像排障大作战**（本日重头戏！）：
   - EOF错误 → 发现是Clash代理出口到docker.io CDN有问题！**禁用代理走直连** → hello-world秒拉成功！
   - minio/minio镜像真相：Docker Hub仓库**404整个没了**！quay.io **401私有**！DaoCloud denied！
   - **华为云SWR同步站**拉MinIO成功！（`swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/minio/minio:RELEASE.2024-10-29T16-01-48Z`）
   - etcd用quay.io直连成功！（之前TLS超时也是代理坑的！）
7. 写了docker-compose-milvus.yml，**标准三件套**（etcd+MinIO+Milvus三个容器！）
8. `docker compose up -d` → 三个容器全部healthy！
9. 重跑day19/milvus_server_rag.py（**零改动！**）→ 完整6环节RAG在三件套上跑通！答案正确！
10. 深挖概念：镜像/容器/Dockerfile、三件套分工、集群/副本、Milvus vs MySQL

---

## Docker核心概念

### 1. Docker三件套（面试必答！）
- **镜像（Image）** = 模板！（只读！含完整环境：操作系统+软件+依赖！）
- **容器（Container）** = 实例！（镜像跑起来的进程！可启停！）
- **Dockerfile** = 配方！（怎么构建镜像的说明书！）
- 类比：镜像=安装包模板！容器=安装好的软件！Dockerfile=制作安装包的步骤！

### 2. Docker不是数据库！是容器平台！
```
Docker = 容器平台！（通用运行时！只管拉镜像+跑容器！）
镜像内容/仓库开放 = 镜像提供方的事！（MinIO官方！）
类比：Docker=快递公司！MinIO=商家！快递不保证商家还卖不卖货！
```
- "Docker会把配置都配好"是误解！Docker只保证拉取机制！拉不拉得到是发布方决定的！

### 3. Docker Compose（多容器编排！）
```yaml
# docker-compose-milvus.yml 核心结构
services:
  etcd:        # 记账员！元数据！
    image: quay.io/coreos/etcd:v3.5.5
  minio:       # 冷库！对象存储！
    image: minio/minio:latest
  standalone:  # 前台！Milvus主程序！
    image: milvusdb/milvus:latest
```
- 一条命令起全部：`docker compose -f docker-compose-milvus.yml up -d`
- 有depends_on（依赖顺序！etcd/MinIO先起，Milvus后起！）+ healthcheck（健康检查！）

### 4. 标准三件套分工（谁在干嘛？）
```
你 → 只连Milvus（19530端口！存向量！查相似！）
Milvus内部：
  → etcd（账本！） 存元数据："哪个collection？数据在MinIO哪？"
  → MinIO（仓库！）存真实数据："向量+原文"
类比：Milvus=前台（干活！）etcd=账本（记位置！）MinIO=仓库（放内容！）
```

### 5. 集群概念（分布式！）
- **数据分片（sharding）**：把数据切成很多份！每台机器存一份！（1亿条→10台→每台1000万！）
- **并行查询**：所有机器同时查自己的部分！协调者汇总！（10个人一起找比1个人快！）
- **副本（replica）**：同一份数据复制几份放不同机器！（一台挂了其他还在！数据不丢！）
- ⚠️ 我们搭的三件套是**单机演示版**（学原理！）真正分片+副本是企业集群版！

### 6. Milvus vs MySQL（不是替代！是互补！）
```
MySQL = 关系型！存精确数据！（用户/订单！WHERE id=123！）
Milvus = 向量库！存AI向量！（语义搜索！找"意思最像"的！）
AI应用两个都要用！（业务数据→MySQL！内容向量→Milvus！）
```

### 7. 镜像为什么那么大？
```
镜像 = 操作系统层 + 软件本身 + 依赖库！（完整环境包！）
hello-world=几KB！etcd=273MB！MinIO=227MB！
Milvus=2.19GB！（分布式数据库！一个镜像打包所有角色：协调器/数据节点/查询节点！）
```

---

## 今天学到了什么关键点？

### 1. 排障方法论（最值钱！）：先分"网络问题"还是"仓库问题"！
```
EOF / TLS timeout / connection reset → 网络问题！
  → 查代理！试直连！试加速器！
404 / 401 / denied / manifest not found → 仓库问题！
  → 用API验证仓库是否存在！搜替代源！
两层可能同时存在！互相掩盖！要拆开验证！
（用最小的hello-world测网络！用API查仓库！）
```

### 2. 国内镜像源分两类！
```
加速器（中科大/163/腾讯）= 转发docker.io！（不存镜像！）
  → 2024年后陆续停止公共服务！（Docker Hub调整中国区服务！）
同步站（阿里云/DaoCloud/华为云SWR）= 拷贝镜像到国内云！
  → 源（Docker Hub）没了 → 同步缓存被清！
  → 华为云SWR的ddn-k8s = 还没被清理的旧同步！（运气！）
```

### 3. API兼容的价值！（企业为什么爱标准化！）
- 单容器模式 → 标准三件套！**底层架构换了！程序零改动！**
- day19/milvus_server_rag.py一个字没改！直接跑通！（都是连localhost:19530！API一样！）

### 4. 镜像/数据怎么处理？
```
镜像 → 存在Docker本地仓库！（不在文件夹！docker images看！）
数据 → day20/volumes/！（.gitignore已忽略！）
GitHub只传"配方"（代码+Dockerfile+compose+总结）！不传大文件！
（GitHub单文件限制100MB！镜像2GB传不上去！）
```

### 5. cpolar不用重复做！
- Day 6做过公网穿透！原理一样！Day 20不重复！（穿透Docker服务和穿透普通服务一样！）

---

## 今天遇到了什么问题？

### 1. Docker拉镜像EOF（折腾最久！）
- 走Clash代理拉registry-1.docker.io → EOF！
- curl测试：Clash出口到docker.io CDN有问题！（SSL错！）
- **解法：禁用Docker代理走直连！** registry-1.docker.io国内直连可达！（401是正常V2认证响应！）
- 踩坑：ProxyHTTPMode写空串 → Desktop弹窗报错重置配置！（合法值只有system/manual/disabled！）

### 2. minio/minio镜像denied！（仓库真没了！）
- Docker Hub的minio/minio → **404**！（API验证：整个仓库不存在！）
- quay.io的minio → **401**！（资源未授权！私有/受限！）
- DaoCloud/阿里云同步 → denied！（已被清！）
- **解法：华为云SWR同步站！** swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/minio/minio:RELEASE.2024-10-29T16-01-48Z（227MB！拉到后docker tag成minio/minio:latest！）

### 3. etcd镜像拉不下来！
- 之前quay.io TLS timeout → 同样是代理坑！
- **解法：禁用代理后quay.io直连秒拉！**（273MB！）

### 4. docker compose冲突！
- 旧单容器模式的milvus-standalone容器占用名字！
- 解法：`docker rm milvus-standalone`（删容器！数据卷保留！）再up！

### 5. 中文输出被Windows管道吞！
- 照旧：重定向到文件再Read（python -u + > xxx.log）！

---

## 一句话总结

> **今天把部署搞透了！用Dockerfile打包了自己的Agent（build+run+实测！）、解决了Docker拉镜像两大难题（EOF=代理问题禁用直连！minio仓库没了=华为云SWR同步站救场！）、用Docker Compose把Milvus标准三件套（etcd记账+MinIO存储+Milvus计算）搭起来全部healthy、day19的RAG程序零改动直接跑通！还搞懂了集群（分片+并行+副本）、Milvus vs MySQL（互补不替代）、镜像为什么大（完整环境包）！**

---

## 明天学什么？

Day 21！评测Agent效果（怎么知道Agent好不好用？怎么评测对话质量/工具调用准确率/RAG效果？常用评测工具！）
