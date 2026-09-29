# ============================================================
# day16/chunking_demo.py - 分块技巧演示
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("分块技巧演示")
    print("=" * 50)
    
    # 1. 一个长文档！
    long_text = """
    什么是GDP？
    GDP是国内生产总值的简称！是指一个国家在一定时期内生产的所有最终产品和服务的市场价值！
    GDP是衡量一个国家经济状况的重要指标！
    
    什么是CPI？
    CPI是居民消费价格指数的简称！是反映居民家庭一般所购买的消费品和服务项目价格水平变动情况的宏观经济指标！
    CPI是衡量通货膨胀的重要指标！
    
    什么是PPI？
    PPI是工业生产者出厂价格指数的简称！是反映工业企业产品出厂价格变动趋势和变动程度的指数！
    PPI是衡量工业企业产品价格变动情况的重要指标！
    
    什么是RAG？
    RAG是检索增强生成的简称！是一种从外部知识库检索信息，然后让大模型根据检索到的信息生成回答的技术！
    RAG可以解决大模型知识过时的问题！
    
    什么是Agent？
    Agent是智能体的简称！是一种能够自主感知环境、做出决策、执行行动的AI系统！
    Agent可以自己决定要不要调用工具！
    
    什么是LangChain？
    LangChain是一个用于开发大模型应用的框架！它提供了很多工具，比如Chain、Agent、RAG等等！
    LangChain可以让我们快速开发大模型应用！
    """
    
    print("原始文档长度：", len(long_text))
    print()
    
    # 2. 分块！
    print("开始分块...")
    
    # 方法1：简单分块！每200个字符一块！
    text_splitter1 = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    chunks1 = text_splitter1.split_text(long_text)
    print(f"方法1：每200个字符一块，分成了{len(chunks1)}块！")
    for i, chunk in enumerate(chunks1):
        print(f"  块{i+1}：{chunk[:50]}...")
    print()
    
    # 方法2：每500个字符一块！
    text_splitter2 = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks2 = text_splitter2.split_text(long_text)
    print(f"方法2：每500个字符一块，分成了{len(chunks2)}块！")
    for i, chunk in enumerate(chunks2):
        print(f"  块{i+1}：{chunk[:50]}...")
    print()
    
    # 方法3：按标点符号分块！
    text_splitter3 = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
    )
    chunks3 = text_splitter3.split_text(long_text)
    print(f"方法3：按标点符号分块，分成了{len(chunks3)}块！")
    for i, chunk in enumerate(chunks3):
        print(f"  块{i+1}：{chunk[:50]}...")
    print()
    
    # 3. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. chunk_size：每块多大？")
    print("2. chunk_overlap：块之间重叠多少？")
    print("3. separators：按什么符号分块？")
    print()
    print("一般来说：")
    print("- chunk_size：200~500个字符")
    print("- chunk_overlap：20~50个字符")
    print("- separators：先按段落分，再按句子分，最后按词语分")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
