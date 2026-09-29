# ============================================================
# day16/reranking_demo.py - 重排序演示
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

load_dotenv()

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("重排序演示")
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
    
    # 3. 创建向量库！
    print("创建向量库...")
    vector_store = FAISS.from_texts(texts, embeddings)
    
    # 4. 问题！
    question = "什么是GDP？"
    print(f"问题：{question}")
    print()
    
    # 5. 先从向量库里找10个文档！
    print("先从向量库里找10个文档！")
    docs = vector_store.similarity_search(question, k=10)
    for i, doc in enumerate(docs):
        print(f"  文档{i+1}：{doc.page_content[:50]}...")
    print()
    
    # 6. 重排序！
    print("重排序！")
    print("（用硅基流动的bge-reranker-v2-m3模型！）")
    print()
    
    # 7. 调用硅基流动的reranker API！
    import requests
    url = "https://api.siliconflow.cn/v1/rerank"
    headers = {
        "Authorization": f"Bearer {os.getenv('SILICONFLOW_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "BAAI/bge-reranker-v2-m3",
        "query": question,
        "documents": [doc.page_content for doc in docs]
    }
    
    print("调用reranker API...")
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    print("重排序结果：")
    for i, item in enumerate(result["results"]):
        print(f"  第{i+1}名：{docs[item['index']].page_content[:50]}...（分数：{item['relevance_score']:.4f}）")
    print()
    
    # 8. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 先从向量库里找10个文档！")
    print("2. 然后用reranker模型重新排序！")
    print("3. 把最相关的排在前面！")
    print("4. 然后只取前3个！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
