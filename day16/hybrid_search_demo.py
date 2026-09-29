# ============================================================
# day16/hybrid_search_demo.py - 混合搜索演示
# 向量搜索 + 关键词搜索！
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ============================================================
# 关键词搜索（不用向量！直接找词语！）
# ============================================================

def keyword_search(question, texts):
    """关键词搜索：找包含问题里词语的文档！"""
    # 把问题里的标点去掉！分成词语！
    words = []
    for char in question:
        if char not in "，。！？、：；""''（）":
            words.append(char)
    
    # 给每个文档打分！包含的词语越多，分数越高！
    results = []
    for i, text in enumerate(texts):
        score = 0
        for word in words:
            if word in text:
                score += 1
        if score > 0:
            results.append((score, i, text))
    
    # 按分数从高到低排序！
    results.sort(reverse=True)
    return results


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("混合搜索演示")
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
    
    # 5. 向量搜索！找3个文档！
    print("【第1步】向量搜索！找3个文档！")
    vector_docs = vector_store.similarity_search(question, k=3)
    vector_indices = []
    for i, doc in enumerate(vector_docs):
        # 找到这个文档在texts里的位置！
        index = texts.index(doc.page_content)
        vector_indices.append(index)
        print(f"  向量结果{i+1}：{doc.page_content[:50]}...（texts里的第{index+1}个）")
    print()
    
    # 6. 关键词搜索！找包含词语的文档！
    print("【第2步】关键词搜索！找包含词语的文档！")
    keyword_results = keyword_search(question, texts)
    keyword_indices = []
    for score, index, text in keyword_results:
        keyword_indices.append(index)
        print(f"  关键词结果：{text[:50]}...（分数：{score}，texts里的第{index+1}个）")
    print()
    
    # 7. 合并结果！去重！
    print("【第3步】合并结果！去重！")
    merged = list(dict.fromkeys(vector_indices + keyword_indices))
    print(f"  合并后一共有{len(merged)}个文档：")
    for i, index in enumerate(merged):
        print(f"  第{i+1}个：{texts[index][:50]}...（texts里的第{index+1}个）")
    print()
    
    # 8. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 向量搜索：理解意思！")
    print("2. 关键词搜索：精确匹配！")
    print("3. 合并结果！去重！")
    print()
    print("为什么两个都要？")
    print("向量搜索理解意思！但是精确的词语匹配不行！")
    print("关键词搜索精确匹配！但是理解不了意思！")
    print("两个都要！效果最好！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
