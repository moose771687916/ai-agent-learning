# -*- coding: utf-8 -*-
"""
Day 19 - Milvus Lite 入门
企业级向量数据库 Milvus 的轻量版（API 与正式版完全一致！）

本demo演示：连接 → 建库 → 插入数据 → 向量检索 全流程
"""

from pymilvus import MilvusClient

# ============ 1. 连接Milvus（Lite版=本地文件；正式版=连接服务器）============
# 正式版（Docker部署）：client = MilvusClient(uri="http://localhost:19530")
# Lite版（学习用）：    client = MilvusClient("milvus_demo.db")  ← 在本地生成一个数据库文件！
print("=" * 50)
print("【第1步】连接Milvus")
client = MilvusClient("milvus_demo.db")
print("✅ 连接成功！本地数据库文件：milvus_demo.db")


# ============ 2. 建集合（Collection）= 相当于MySQL里的"表"！============
# 每条数据 = 一个向量（512维）+ 附带文本
# 维度必须和embedding模型输出一致！（我们用512维，和FAISS demo一致！）
print("\n【第2步】创建集合（Collection）")
collection_name = "doc_knowledge"

# 如果集合已存在，先删掉（保证每次重跑都是干净的）
if client.has_collection(collection_name):
    client.drop_collection(collection_name)

# 创建集合：指定名字 + 向量维度
client.create_collection(
    collection_name=collection_name,
    dimension=512          # 每条向量的维度
)
print(f"✅ 集合 '{collection_name}' 创建成功！（维度=512）")


# ============ 3. 准备数据（模拟embedding后的文档！）============
# 真实场景：文档 → embedding模型 → 512维向量！
# 这里模拟：写10条文档，手工造出"相关文档向量接近"的效果！
# 关键：主题A的向量都"靠近"主题A！主题B的向量都"靠近"主题B！
print("\n【第3步】准备数据（模拟embedding）")

def make_doc_vector(base_idx, jitter=0.01):
    """造一个512维向量：以base_idx位置为"热点"，其他位置随机小值"""
    import random
    random.seed(base_idx * 100)
    vec = [random.uniform(0, 0.01) for _ in range(512)]
    # 在特定位置放一个"峰值"，让同类文档有共同特征
    vec[base_idx % 512] = 0.95
    vec[(base_idx + 1) % 512] = 0.90
    vec[(base_idx + 2) % 512] = 0.85
    return vec

# 10篇文档：汽车主题（idx 10-19区）、美食主题（idx 100区）、旅游主题（idx 200区）
docs = [
    # (id, 文本内容, 热点位置)
    (1, "新能源汽车电池采用磷酸铁锂技术，续航可达600公里", 10),
    (2, "车载智能系统支持语音控制，可自动规划导航路线", 12),
    (3, "特斯拉Model Y采用一体压铸车身，大幅降低制造成本", 14),
    (4, "小米SU7搭载900V高压平台，充电15分钟续航500公里", 16),
    (5, "自动驾驶技术依赖激光雷达与高精地图的配合", 18),
    (6, "火锅底料选用牛油制作，麻辣鲜香，适合朋友聚餐", 100),
    (7, "重庆小面讲究面条筋道，红油辣椒是灵魂", 102),
    (8, "广式早茶包含虾饺、烧卖、肠粉等经典点心", 104),
    (9, "北京故宫博物院收藏文物186万余件，是世界文化遗产", 200),
    (10, "桂林山水甲天下，漓江竹筏漂流是最受欢迎的体验", 202),
]

# 插入数据：id + 向量 + 原文（方便检索后回看内容！）
data = []
for doc_id, text, base_idx in docs:
    vec = make_doc_vector(base_idx)
    data.append({
        "id": doc_id,          # 主键
        "vector": vec,         # 512维向量
        "text": text           # 原文（附加字段！检索后能拿到！）
    })

client.insert(collection_name=collection_name, data=data)
print(f"✅ 已插入 {len(data)} 条文档数据！")


# ============ 4. 向量检索：问一个问题 → 变向量 → 找最像的！============
print("\n【第4步】向量检索")
print("-" * 50)

# 模拟用户问题："电动车电池充电快吗？" → embedding模型 → 向量
# 这里手工造一个"靠近汽车电池主题"的查询向量（热点在10附近！）
import random
random.seed(999)
query_vec = [random.uniform(0, 0.01) for _ in range(512)]
query_vec[10] = 0.95    # 和"新能源汽车电池"（doc 1，热点10）最像！
query_vec[11] = 0.85
query_vec[16] = 0.80    # 和"小米SU7充电"（doc 4，热点16）也像！

results = client.search(
    collection_name=collection_name,
    data=[query_vec],          # 查询向量
    limit=3,                   # 返回最像的3条
    output_fields=["text"]     # 顺带返回原文
)

print(f"查询向量：热点在位置10、11、16（模拟'电动车电池充电'）")
print(f"检索结果（最像的3条）：\n")
for i, hit in enumerate(results[0]):
    print(f"  #{i+1} 相似度={hit['distance']:.4f}  id={hit['id']}")
    print(f"      文本: {hit['entity']['text']}")

print("\n" + "=" * 50)
print("🎯 结论：和'电动车电池充电'最相关的两条（doc 1、doc 4）都被找到了！")
print("    这就是RAG的核心：文档→向量→检索→拿原文给大模型！")
