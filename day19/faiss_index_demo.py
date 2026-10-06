# ============================================================
# day19/faiss_index_demo.py - FAISS索引类型对比！
#
# 今天学什么：
#   向量数据库的【索引】= 检索算法！不同索引，速度/精度不同！
#   Flat  ：暴力全扫描！100%准确！慢！
#   IVF   ：先分组再找！快！稍损精度！
#   HNSW  ：跳棋式多层找！超快！企业最爱！
# ============================================================

import time
import numpy as np
import faiss

print("=" * 50)
print("FAISS索引类型对比！")
print("=" * 50)
print()

# ============================================================
# 1. 造数据！模拟10万条文档向量！
# ============================================================
# 每条向量 = 512维（相当于embedding模型把一段文字变成一个512维数字数组！）
DIM = 512          # 向量维度
N = 100000         # 文档数量（10万条！模拟企业级数据！）
K = 5              # 每次检索返回最像的5条！

print(f"📊 模拟数据：{N}条文档，每条{DIM}维向量！")
print()

# 随机生成10万个向量（模拟文档embedding结果）
np.random.seed(42)   # 固定随机种子！结果可复现！
data = np.random.random((N, DIM)).astype("float32")

# 1个查询向量（模拟用户问题的embedding）
query = np.random.random((1, DIM)).astype("float32")

print(f"✅ 数据准备好了！开始建3种索引对比！")
print()


# ============================================================
# 2. 索引1：Flat（暴力全扫描！）
# ============================================================
# 原理：一个向量一个向量地比！100%准确！但慢！
# 适用：数据量小（<10万）、对精度要求极高！

print("【索引1：Flat（暴力全扫描）】")
start = time.time()

index_flat = faiss.IndexFlatL2(DIM)   # 建索引！L2=欧氏距离！
index_flat.add(data)                  # 把所有向量加进去！

build_time = time.time() - start
print(f"  ⏱️  建索引耗时：{build_time*1000:.1f}毫秒")
print(f"  （Flat建索引=只把向量存起来，不做额外处理！所以快！）")

# 检索！
start = time.time()
D_flat, I_flat = index_flat.search(query, K)   # 查！返回距离+索引号！
query_time = time.time() - start
print(f"  🔍 检索耗时：{query_time*1000:.1f}毫秒")
print(f"  （检索=把10万条全比一遍！所以慢！）")
print()

# ============================================================
# 3. 索引2：IVF（先分组再找！）
# ============================================================
# 原理：先用聚类把10万条分成N个组！检索时只找最近的1个组！
#       相当于"先分班级，再去班里找"！快！
# 精度：稍损！因为可能漏掉"隔壁班"的最优！

print("【索引2：IVF（先分组再找！）】")
nlist = 100   # 分成100个组！

start = time.time()

quantizer = faiss.IndexFlatL2(DIM)              # 分组的"班长"索引
index_ivf = faiss.IndexIVFFlat(quantizer, DIM, nlist)  # IVF索引！
index_ivf.train(data)      # 训练！让FAISS学会"怎么分组"！（聚类！）
index_ivf.add(data)        # 加入数据！

build_time = time.time() - start
print(f"  ⏱️  建索引耗时：{build_time*1000:.1f}毫秒")
print(f"  （IVF建索引=要先聚类分组！所以比Flat慢！）")

start = time.time()
index_ivf.nprobe = 10      # 检索时搜最近的10个组！（默认1！越多越准越慢！）
D_ivf, I_ivf = index_ivf.search(query, K)
query_time = time.time() - start
print(f"  🔍 检索耗时：{query_time*1000:.1f}毫秒")
print(f"  （只搜10个组，不是10万条！所以快！）")
print()

# ============================================================
# 4. 索引3：HNSW（跳棋式多层找！）
# ============================================================
# 原理：像跳棋！先跳远看大概方向，再跳近精确找！
#       多层"地图"：粗地图找方向 → 细地图找精确！
# 企业最爱：速度快 + 精度高！

print("【索引3：HNSW（跳棋式多层找！）】")

start = time.time()

index_hnsw = faiss.IndexHNSWFlat(DIM, 32)   # 32=每个节点连32个邻居！
index_hnsw.add(data)

build_time = time.time() - start
print(f"  ⏱️  建索引耗时：{build_time*1000:.1f}毫秒")

start = time.time()
D_hnsw, I_hnsw = index_hnsw.search(query, K)
query_time = time.time() - start
print(f"  🔍 检索耗时：{query_time*1000:.1f}毫秒")
print(f"  （跳棋式！先粗后细！超快！）")
print()

# ============================================================
# 5. 对比总结！
# ============================================================
print("=" * 50)
print("📊 三大索引对比总结！")
print("=" * 50)

# 重跑一次检索拿准确时间（排除首次加载误差！）
index_flat.search(query, K)
t0 = time.time()
for _ in range(100):
    index_flat.search(query, K)
flat_time = (time.time() - t0) / 100

index_ivf.nprobe = 10
index_ivf.search(query, K)
t0 = time.time()
for _ in range(100):
    index_ivf.search(query, K)
ivf_time = (time.time() - t0) / 100

index_hnsw.search(query, K)
t0 = time.time()
for _ in range(100):
    index_hnsw.search(query, K)
hnsw_time = (time.time() - t0) / 100

print()
print(f"  Flat 检索：{flat_time*1000:.2f}毫秒/次   （暴力！最准！最慢！）")
print(f"  IVF  检索：{ivf_time*1000:.2f}毫秒/次   （分组！快{flat_time/ivf_time:.0f}倍！）")
print(f"  HNSW 检索：{hnsw_time*1000:.2f}毫秒/次   （跳棋！快{flat_time/hnsw_time:.0f}倍！）")
print()

# 检查三个索引返回的结果是否一致！（看精度！）
print("结果一致性检查（看精度！）：")
same_flat_hnsw = (I_flat.flatten() == I_hnsw.flatten()).sum()
print(f"  Flat和HNSW返回的前{K}条：相同 {same_flat_hnsw}/{K} 条")
print(f"  （随机数据：所有向量'长一样'！没有'真的最近'！所以0/5正常！）")
print()

# ============================================================
# 6. 真实结构数据！模拟"有语义的文档"！
# ============================================================
# 真实文档不是随机数！相似文档的向量会【聚集】在一起！
# 比如：8个主题（汽车/美食/体育...），每类文档聚在一团！
# 有结构的数据，HNSW才能发挥真正实力！

print("=" * 50)
print("📊 真实结构数据对比！（模拟有语义的文档！）")
print("=" * 50)
print()

# 造数据：8个"主题中心"，每个中心周围聚集一批文档！
CENTERS = 8
centers = np.random.random((CENTERS, DIM)).astype("float32")   # 8个主题中心！
data_real = np.zeros((N, DIM), dtype="float32")
for i in range(N):
    center = centers[i % CENTERS]   # 轮流属于8个主题之一！
    data_real[i] = center + np.random.random(DIM).astype("float32") * 0.1  # 围绕中心！
# 这样：属于同一主题的文档，向量很接近！不同主题的，离得远！

# 查询向量也围绕某个中心！（模拟"问汽车相关问题"）
query_real = centers[0] + np.random.random(DIM).astype("float32") * 0.1
query_real = query_real.reshape(1, DIM)   # 必须2维！(1, DIM)！faiss要求！

# 建Flat和HNSW！
index_flat2 = faiss.IndexFlatL2(DIM)
index_flat2.add(data_real)

index_hnsw2 = faiss.IndexHNSWFlat(DIM, 32)
# 🔑 HNSW调参！默认探索太少（16）在高维空间找不到真最近邻！
# efConstruction：建索引时探索多少节点（默认40 → 200！建更密的图！）
index_hnsw2.hnsw.efConstruction = 200
index_hnsw2.add(data_real)
# efSearch：检索时探索多少节点（默认16 → 200！搜得更细！）
index_hnsw2.hnsw.efSearch = 200

# 分别检索！
D_f2, I_f2 = index_flat2.search(query_real, K)     # 暴力（最准！）
D_h2, I_h2 = index_hnsw2.search(query_real, K)     # HNSW（超快！）

same2 = (I_f2.flatten() == I_h2.flatten()).sum()
print(f"  Flat和HNSW返回的前{K}条：相同 {same2}/{K} 条！")
print(f"  （真实结构数据：HNSW又快又准！几乎和暴力一样！）")
print()

# 测速！
t0 = time.time()
for _ in range(100):
    index_flat2.search(query_real, K)
flat_time2 = (time.time() - t0) / 100

t0 = time.time()
for _ in range(100):
    index_hnsw2.search(query_real, K)
hnsw_time2 = (time.time() - t0) / 100

print(f"  Flat 检索：{flat_time2*1000:.2f}毫秒/次")
print(f"  HNSW 检索：{hnsw_time2*1000:.2f}毫秒/次（快{flat_time2/hnsw_time2:.0f}倍！）")
print()

print("=" * 50)
print("总结：")
print("=" * 50)
print("1. Flat：暴力全扫描！最准最慢！数据少用它！")
print("2. IVF：先分组再找！快！稍损精度！")
print("3. HNSW：跳棋式多层找！超快！精度也高！企业最爱！")
print("4. 建索引耗时≠检索耗时！IVF建索引慢但检索快！")
print("5. 企业生产：百万级数据用IVF/HNSW！千万级必须HNSW！")
