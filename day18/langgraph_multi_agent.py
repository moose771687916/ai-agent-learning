# ============================================================
# day18/langgraph_multi_agent.py - 多Agent协作！
# 两个大模型Agent协作干活：研究Agent + 写作Agent！
# ============================================================

from typing import TypedDict
from dotenv import load_dotenv
import os
from openai import OpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ============================================================
# 1. 定义状态
# ============================================================

class State(TypedDict):
    """状态：图里所有节点共享的数据！"""
    topic: str              # 用户给的主题
    research_points: str    # 研究Agent产出的要点
    article: str            # 写作Agent产出的文章


# ============================================================
# 2. 创建大模型客户端
# ============================================================

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

def call_model(system_prompt: str, user_content: str) -> str:
    """调用大模型！"""
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    )
    return response.choices[0].message.content


# ============================================================
# 3. 定义Agent节点！
# 每个节点 = 一个独立的大模型Agent！
# ============================================================

def research_agent(state: State) -> State:
    """Agent 1：研究Agent！根据主题，产出研究要点！"""
    topic = state["topic"]
    print(f"  [研究Agent] 收到主题：{topic}")
    print(f"  [研究Agent] 正在研究...")
    
    points = call_model(
        "你是一个资深研究员！请根据用户给出的主题，产出3-5条核心研究要点！每条一行！用数据说话！",
        f"主题：{topic}"
    )
    
    print(f"  [研究Agent] 研究完成！要点：")
    print(f"    {points}")
    return {"research_points": points}


def write_agent(state: State) -> State:
    """Agent 2：写作Agent！根据研究要点，写出完整文章！"""
    points = state["research_points"]
    print(f"  [写作Agent] 收到研究要点！")
    print(f"  [写作Agent] 正在写文章...")
    
    article = call_model(
        "你是一个资深编辑！请根据研究要点，写一篇500字左右的完整文章！结构清晰！有标题！有段落！",
        f"研究要点如下：\n{points}"
    )
    
    print(f"  [写作Agent] 写完了！")
    return {"article": article}


# ============================================================
# 4. 画图！两个Agent串起来！
# ============================================================

def main():
    print("=" * 50)
    print("多Agent协作（研究Agent + 写作Agent）")
    print("=" * 50)
    
    # 1. 创建图！
    graph = StateGraph(State)
    
    # 2. 添加节点！（两个大模型Agent！）
    graph.add_node("research", research_agent)  # 研究Agent！
    graph.add_node("write", write_agent)        # 写作Agent！
    
    # 3. 添加边！
    graph.add_edge(START, "research")  # 开始 → 研究Agent
    graph.add_edge("research", "write")  # 研究Agent → 写作Agent
    graph.add_edge("write", END)       # 写作Agent → 结束
    
    # 4. 编译！
    app = graph.compile()
    
    print("图的结构：开始 → [研究Agent] → [写作Agent] → 结束")
    print()
    
    # 5. 运行！（用户给主题！）
    print("【运行图】用户主题：人工智能在汽车行业的应用")
    result = app.invoke({"topic": "人工智能在汽车行业的应用"})
    print()
    
    # 6. 展示最终文章！
    print("=" * 50)
    print("【最终文章】")
    print("=" * 50)
    print(result["article"])
    print()
    
    # 7. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 每个节点 = 一个独立的大模型Agent！")
    print("2. 研究Agent：主题 → 研究要点！")
    print("3. 写作Agent：研究要点 → 文章！")
    print("4. 两个Agent通过图协作！前一个的输出！是后一个的输入！")
    print("5. 这就是多Agent协作！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
