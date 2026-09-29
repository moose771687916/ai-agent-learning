# ============================================================
# day16/multi_query_rag.py - 多查询RAG演示
# 同一个问题，用多种方式问！
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("多查询RAG演示")
    print("=" * 50)
    
    # 1. 创建大模型（用来改写问题！）
    llm = ChatOpenAI(
        model="glm-4-flash",
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 2. 创建embedding模型
    embeddings = OpenAIEmbeddings(
        model="BAAI/bge-m3",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 3. 自己创建知识！
    texts = [
        "GDP是国内生产总值的简称！是指一个国家在一定时期内生产的所有最终产品和服务的市场价值！",
        "CPI是居民消费价格指数的简称！是反映居民家庭一般所购买的消费品和服务项目价格水平变动情况的宏观经济指标！",
        "PPI是工业生产者出厂价格指数的简称！是反映工业企业产品出厂价格变动趋势和变动程度的指数！",
        "RAG是检索增强生成的简称！是一种从外部知识库检索信息，然后让大模型根据检索到的信息生成回答的技术！",
        "Agent是智能体的简称！是一种能够自主感知环境、做出决策、执行行动的AI系统！",
        "LangChain是一个用于开发大模型应用的框架！它提供了很多工具，比如Chain、Agent、RAG等等！",
    ]
    
    # 4. 创建向量库！
    print("创建向量库...")
    vector_store = FAISS.from_texts(texts, embeddings)
    
    # 5. 用户问题！
    question = "什么是GDP？"
    print(f"用户问题：{question}")
    print()
    
    # 6. 让大模型把问题改写成3个不同的问法！
    print("【第1步】让大模型把问题改写成3个不同的问法！")
    rewrite_prompt = f"""
请把下面的问题改写成3个不同说法的问题！
要求：
1. 意思一样！
2. 用词不一样！
3. 有的用简称！有的用全称！

原问题：{question}

请只输出3个问题，每行一个！
"""
    response = llm.invoke(rewrite_prompt)
    queries = [q.strip() for q in response.content.split("\n") if q.strip()]
    queries.insert(0, question)  # 把原问题也加上！
    
    print(f"一共{len(queries)}个问题：")
    for i, q in enumerate(queries):
        print(f"  问题{i+1}：{q}")
    print()
    
    # 7. 每个问题都去检索！
    print("【第2步】每个问题都去检索！")
    all_results = []
    for q in queries:
        docs = vector_store.similarity_search(q, k=2)
        for doc in docs:
            if doc.page_content not in all_results:
                all_results.append(doc.page_content)
        print(f"  问题「{q}」检索到了：")
        for doc in docs:
            print(f"    - {doc.page_content[:40]}...")
    print()
    
    # 8. 合并结果！去重！
    print(f"【第3步】合并结果！去重！一共{len(all_results)}个文档！")
    for i, text in enumerate(all_results):
        print(f"  第{i+1}个：{text[:50]}...")
    print()
    
    # 9. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 用户只问一遍！")
    print("2. 让大模型改写成多个问法！")
    print("3. 每个问法都去检索！")
    print("4. 合并结果！去重！")
    print()
    print("为什么这样效果好？")
    print("因为不同问法，检索出来的结果不一样！")
    print("'GDP'可能检索不到！但是'国内生产总值'可能检索得到！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
