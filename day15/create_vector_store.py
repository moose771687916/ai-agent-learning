# ============================================================
# day15/create_vector_store.py - 自己创建知识！然后建向量库！
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
    print("自己创建知识！然后建向量库！")
    print("=" * 50)
    
    # 1. 创建embedding模型
    embeddings = OpenAIEmbeddings(
        model="BAAI/bge-m3",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 2. 自己创建知识！
    texts = [
        "GDP是国内生产总值的简称！是指一个国家在一定时期内生产的所有最终产品和服务的市场价值！",
        "CPI是居民消费价格指数的简称！是反映居民家庭一般所购买的消费品和服务项目价格水平变动情况的宏观经济指标！",
        "PPI是工业生产者出厂价格指数的简称！是反映工业企业产品出厂价格变动趋势和变动程度的指数！",
        "RAG是检索增强生成的简称！是一种从外部知识库检索信息，然后让大模型根据检索到的信息生成回答的技术！",
        "Agent是智能体的简称！是一种能够自主感知环境、做出决策、执行行动的AI系统！",
        "LangChain是一个用于开发大模型应用的框架！它提供了很多工具，比如Chain、Agent、RAG等等！",
    ]
    
    # 3. 用这些知识创建向量库！
    print("创建向量库...")
    vector_store = FAISS.from_texts(texts, embeddings)
    
    # 4. 保存向量库！
    print("保存向量库...")
    vector_store.save_local("./faiss_index_day15")
    
    print("完成！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
