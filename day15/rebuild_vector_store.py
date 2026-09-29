# ============================================================
# day15/rebuild_vector_store.py - 重建向量库
# 用新的embedding模型（bge-large-zh-v1.5）！
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("重建向量库")
    print("=" * 50)
    
    # 1. 旧的embedding模型
    old_embeddings = OpenAIEmbeddings(
        model="BAAI/bge-m3",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 2. 加载旧的向量库
    print("加载旧的向量库...")
    old_vector_store = FAISS.load_local(
        "../day07/faiss_index",
        old_embeddings,
        allow_dangerous_deserialization=True
    )
    
    # 3. 从旧的向量库里把文档拿出来！
    print("从旧的向量库里拿文档...")
    documents = old_vector_store.similarity_search("什么是RAG", k=100)
    print(f"拿到了{len(documents)}个文档块！")
    
    # 4. 新的embedding模型
    new_embeddings = OpenAIEmbeddings(
        model="BAAI/bge-large-zh-v1.5",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 5. 用新的embedding模型创建新的向量库！
    print("创建新的向量库...")
    new_vector_store = FAISS.from_documents(documents, new_embeddings)
    
    # 6. 保存新的向量库！
    print("保存新的向量库...")
    new_vector_store.save_local("./faiss_index_new")
    
    print("完成！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
