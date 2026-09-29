# ============================================================
# day16/rag_eval_demo.py - RAG评测演示
# 怎么知道RAG好不好用？
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
    print("RAG评测演示")
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
    
    # 4. 准备测试集！（问题和正确答案！）
    test_set = [
        {"question": "什么是GDP？", "answer": "GDP是国内生产总值的简称"},
        {"question": "什么是CPI？", "answer": "CPI是居民消费价格指数的简称"},
        {"question": "什么是PPI？", "answer": "PPI是工业生产者出厂价格指数的简称"},
        {"question": "什么是RAG？", "answer": "RAG是检索增强生成的简称"},
        {"question": "什么是Agent？", "answer": "Agent是智能体的简称"},
        {"question": "什么是LangChain？", "answer": "LangChain是一个用于开发大模型应用的框架"},
    ]
    
    print(f"测试集：一共{len(test_set)}个问题！")
    print()
    
    # 5. 每个问题都去检索！看能不能命中！
    print("【评测开始】")
    hit_count = 0
    for i, item in enumerate(test_set):
        question = item["question"]
        answer = item["answer"]
        
        # 检索！找前3个！
        docs = vector_store.similarity_search(question, k=3)
        
        # 看正确答案在不在检索结果里！
        hit = False
        for doc in docs:
            if answer in doc.page_content:
                hit = True
                break
        
        if hit:
            hit_count += 1
            result = "✓ 命中"
        else:
            result = "✗ 没命中"
        
        print(f"  {i+1}. {question}")
        print(f"     正确答案：{answer}...")
        print(f"     检索结果：{result}")
        for j, doc in enumerate(docs):
            print(f"       {j+1}. {doc.page_content[:40]}...")
        print()
    
    # 6. 算命中率！
    hit_rate = hit_count / len(test_set) * 100
    print("=" * 50)
    print(f"【评测结果】")
    print(f"  命中：{hit_count}/{len(test_set)}")
    print(f"  命中率：{hit_rate:.0f}%")
    print()
    
    # 7. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 准备一组问题和正确答案（测试集）！")
    print("2. 每个问题都去检索！")
    print("3. 看正确答案在不在检索结果里！")
    print("4. 算命中率！")
    print()
    print("命中率越高！RAG越好用！")
    print("如果命中率低！就要优化分块、重排序、混合搜索！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
