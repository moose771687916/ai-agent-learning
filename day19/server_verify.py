# -*- coding: utf-8 -*-
"""真Milvus Server验证：连接→建集合→插入→检索"""
from pymilvus import MilvusClient

print("=" * 50)
print("真Milvus Server 验证（Docker部署！）")
print("=" * 50)

# ① 连接（注意：Server版连接地址！不是.db文件！）
c = MilvusClient("http://localhost:19530")
print("① 连接成功：http://localhost:19530 ✅")

# ② 建集合
COLLECTION = "server_test"
if c.has_collection(COLLECTION):
    c.drop_collection(COLLECTION)
c.create_collection(collection_name=COLLECTION, dimension=8)
print("② 建集合成功：server_test（8维）✅")

# ③ 插入
c.insert(COLLECTION, [
    {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], "text": "第一条：数据从0.1开始"},
    {"id": 2, "vector": [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], "text": "第二条：数据从0.8开始"},
])
print("③ 插入2条数据 ✅")
c.flush(COLLECTION)   # 重要！把内存缓冲区的数据提交落盘！
print("   flush（提交落盘）完成 ✅")

# ④ 加载到内存 + 检索（和第一条最像的应该是第一条自己！）
c.load_collection(COLLECTION)
print("   load_collection完成 ✅")
r = c.search(COLLECTION, data=[[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]], limit=2, output_fields=["text"])
print("   search返回原始内容:", r)
print("   命中数量:", len(r[0]) if r else "空")
print("④ 检索结果：")
for h in r[0]:
    print(f"   id={h['id']} | text={h['entity']['text']} | 相似度={h['distance']:.4f}")
print()
print("🎉 真Milvus Server（Docker部署）验证通过！！")
print("   这就是企业部署形态：数据在服务器上！任何程序都能连！")
