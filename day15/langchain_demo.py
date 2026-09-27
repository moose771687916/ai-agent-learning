# ============================================================
# day15/langchain_demo.py - LangChain深入
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# ============================================================
# 第1个：最简单的LangChain
# ============================================================

def demo1_simple():
    print("=" * 50)
    print("Demo 1：最简单的LangChain")
    print("=" * 50)
    
    # 1. 创建大模型
    llm = ChatOpenAI(
        model="glm-4-flash",
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 2. 提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的助手"),
        ("user", "{question}")
    ])
    
    # 3. 输出解析器
    output_parser = StrOutputParser()
    
    # 4. 把它们串起来（这就是Chain！）
    chain = prompt | llm | output_parser
    
    # 5. 调用Chain
    result = chain.invoke({"question": "什么是LangChain？用一句话回答"})
    print(f"AI：{result}")
    print()


# ============================================================
# 第2个：带记忆的LangChain
# ============================================================

def demo2_with_memory():
    print("=" * 50)
    print("Demo 2：带记忆的LangChain")
    print("=" * 50)
    
    # 创建大模型
    llm = ChatOpenAI(
        model="glm-4-flash",
        api_key=os.getenv("ZHIPU_API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )
    
    # 对话历史
    messages = []
    
    # 第1轮对话
    messages.append(HumanMessage(content="我叫小明"))
    result = llm.invoke(messages)
    print(f"你：我叫小明")
    print(f"AI：{result.content}")
    
    # 第2轮对话
    messages.append(AIMessage(content=result.content))
    messages.append(HumanMessage(content="我叫什么名字？"))
    result = llm.invoke(messages)
    print(f"你：我叫什么名字？")
    print(f"AI：{result.content}")
    print()


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    demo1_simple()
    demo2_with_memory()
