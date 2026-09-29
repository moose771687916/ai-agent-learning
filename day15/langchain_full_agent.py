# ============================================================
# day15/langchain_full_agent.py - 完整版LangChain Agent
# 既有RAG，又有工具！
# ============================================================

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# ============================================================
# 定义工具
# ============================================================

@tool
def get_weather(city: str) -> str:
    """查询某个城市的天气"""
    return f"{city}今天晴，25度"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，比如 1+1"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except:
        return "计算错误"


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("完整版LangChain Agent（RAG + 工具）")
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
        "./faiss_index_day15",
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    # 4. 创建检索器
    retriever = vector_store.as_retriever()
    
    # 5. 工具列表
    tools = [get_weather, calculate]
    
    # 6. 把工具绑定到大模型上
    llm_with_tools = llm.bind_tools(tools)
    
    # 7. 提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的助手！你可以查知识库，也可以调用工具！"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # 8. 把它们串起来
    chain = prompt | llm_with_tools
    
    # 9. 对话历史
    messages = []
    
    # 10. 对话循环
    while True:
        user_input = input("\n你：")
        if user_input == "退出":
            break
        
        messages.append(HumanMessage(content=user_input))
        
        # 先查知识库！
        print("[正在查知识库...]")
        documents = retriever.invoke(user_input)
        if documents:
            context = "\n".join([doc.page_content for doc in documents])
            print(f"[知识库找到：{context[:100]}...]")
            messages.append(AIMessage(content=f"我在知识库里找到了这些内容：{context}"))
        
        # 循环处理工具调用
        while True:
            result = chain.invoke({"messages": messages})
            
            if not result.tool_calls:
                print(f"AI：{result.content}")
                messages.append(result)
                break
            
            messages.append(result)
            
            for tool_call in result.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                print(f"[调用工具：{tool_name}，参数：{tool_args}]")
                
                if tool_name == "get_weather":
                    tool_result = get_weather.invoke(tool_args)
                elif tool_name == "calculate":
                    tool_result = calculate.invoke(tool_args)
                else:
                    tool_result = "不知道这个工具"
                
                print(f"[工具返回：{tool_result}]")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
