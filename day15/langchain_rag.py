# ============================================================
# day15/langchain_rag.py - 用LangChain写RAG
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("用LangChain写RAG")
    print("=" * 50)
    
    # 1. 创建大模型
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
    
    # 3. 加载向量库
    vector_store = FAISS.load_local(
        "../day07/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    # 4. 创建检索器
    retriever = vector_store.as_retriever()
    
    # 5. 提示词
    prompt = ChatPromptTemplate.from_template("""
请根据下面的上下文回答问题。
如果上下文里没有答案，就说不知道。

上下文：
{context}

问题：
{question}
""")
    
    # 6. 输出解析器
    output_parser = StrOutputParser()
    
    # 7. 把它们串起来（这就是RAG Chain！）
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )
    
    # 8. 问问题
    while True:
        question = input("\n你：")
        if question == "退出":
            break
        
        result = chain.invoke(question)
        print(f"AI：{result}")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
