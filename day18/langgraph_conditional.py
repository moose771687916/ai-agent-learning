# ============================================================
# day18/langgraph_conditional.py - 条件边（流程分叉！）
# 图的好处：根据情况走不同路线！
# ============================================================

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# ============================================================
# 1. 定义状态
# ============================================================

class State(TypedDict):
    """状态"""
    question: str   # 用户的问题
    answer: str     # 答案


# ============================================================
# 2. 定义节点
# ============================================================

def check_node(state: State) -> State:
    """检查节点：看看问题里有没有"天气"！"""
    question = state["question"]
    print(f"  [检查节点] 收到问题：{question}")
    # 不写answer！只做检查！交给条件边决定下一步！
    return {}


def weather_node(state: State) -> State:
    """天气节点：专门回答天气问题！"""
    question = state["question"]
    print(f"  [天气节点] 这是天气问题！我来回答！")
    return {"answer": f"【天气回答】{question} → 今天晴，25度！"}


def general_node(state: State) -> State:
    """普通节点：回答其他问题！"""
    question = state["question"]
    print(f"  [普通节点] 这不是天气问题！我来回答！")
    return {"answer": f"【普通回答】{question} → 这个问题是这样的：先看A，再看B！"}


# ============================================================
# 3. 定义条件边函数！
# 这个函数决定：下一步去哪！
# ============================================================

def route(state: State) -> str:
    """路由函数！根据问题内容，决定下一步去哪个节点！"""
    question = state["question"]
    # 问题里包含"天气" → 去天气节点！
    if "天气" in question:
        print(f"  [路由] 检测到「天气」→ 走天气节点！")
        return "weather"
    # 否则 → 去普通节点！
    else:
        print(f"  [路由] 没有「天气」→ 走普通节点！")
        return "general"


# ============================================================
# 4. 画图！
# ============================================================

def main():
    print("=" * 50)
    print("LangGraph条件边（流程分叉！）")
    print("=" * 50)
    
    # 1. 创建图！
    graph = StateGraph(State)
    
    # 2. 添加节点！
    graph.add_node("check", check_node)     # 检查节点！
    graph.add_node("weather", weather_node) # 天气节点！
    graph.add_node("general", general_node) # 普通节点！
    
    # 3. 添加边！
    graph.add_edge(START, "check")   # 开始 → 检查
    # 条件边！从check出来！根据route函数的返回值决定去哪个节点！
    graph.add_conditional_edges(
        "check",
        route,
        {
            "weather": "weather",  # route返回"weather" → 去weather节点！
            "general": "general",  # route返回"general" → 去general节点！
        }
    )
    graph.add_edge("weather", END)  # 天气节点 → 结束
    graph.add_edge("general", END)  # 普通节点 → 结束
    
    # 4. 编译！
    app = graph.compile()
    
    print("图的结构：开始 → 检查 → (有天气? → 天气 | 没天气? → 普通) → 结束")
    print()
    
    # 5. 测试1：天气问题！
    print("【测试1】输入：北京今天天气怎么样？")
    result1 = app.invoke({"question": "北京今天天气怎么样？"})
    print(f"  结果：{result1['answer']}")
    print()
    
    # 6. 测试2：非天气问题！
    print("【测试2】输入：什么是LangGraph？")
    result2 = app.invoke({"question": "什么是LangGraph？"})
    print(f"  结果：{result2['answer']}")
    print()
    
    # 7. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 条件边：根据情况走不同路线！")
    print("2. 路由函数（route）：决定下一步去哪个节点！")
    print("3. add_conditional_edges：把路由函数和节点对应起来！")
    print("4. 这是while循环做不到的！流程自己能选择！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
