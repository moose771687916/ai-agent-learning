# ============================================================
# day18/langgraph_loop.py - LangGraph循环（图绕圈！）
#
# 新能力：条件边指回自己 = 循环！
# 场景：AI写文案 → 检查字数 → 不够就重写 → 最多5次！
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
    """状态"""
    topic: str          # 写作主题
    draft: str          # 草稿
    attempts: int       # 已经写了几遍！
    final: str          # 最终稿


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
# 3. 节点们
# ============================================================

def write_node(state: State) -> State:
    """写作节点：写一遍文案！"""
    topic = state["topic"]
    attempts = state["attempts"] + 1    # 写一遍，次数+1！
    
    print(f"  [写作节点] 第{attempts}次写作！主题：{topic}")
    
    # 调大模型写！要求按当前次数递增字数！
    draft = call_model(
        "你是一个文案写手！请写一段文案！要完整！要生动！",
        f"主题：{topic}，请写一段至少{attempts * 30}字的文案！"
    )
    
    print(f"  [写作节点] 写完了！当前字数：{len(draft)}字")
    return {"draft": draft, "attempts": attempts}


def route(state: State) -> str:
    """路由：检查！不够就回去重写！够了就结束！"""
    draft = state["draft"]
    attempts = state["attempts"]
    
    # 第1遍：强制重写！（为了让你明确看到"循环"！）
    if attempts == 1:
        print(f"  [路由] 第1遍（{len(draft)}字）！强制回去重写！让你看看循环！")
        return "again"
    
    # 要求：至少100字！
    if len(draft) < 100 and attempts < 5:
        # 没到100字 且 没写满5次 → 回去再写！（循环！）
        print(f"  [路由] 只有{len(draft)}字，不够100字！回去重写！（第{attempts}次）")
        return "again"
    else:
        # 够了 或 写了5次了 → 结束！
        print(f"  [路由] 达标或已达上限！结束！（{len(draft)}字，第{attempts}次）")
        return "done"


def final_node(state: State) -> State:
    """定稿节点：收尾！"""
    print(f"  [定稿节点] 最终定稿！")
    return {"final": state["draft"]}


# ============================================================
# 4. 画图！关键：条件边指回自己！
# ============================================================

def main():
    print("=" * 50)
    print("LangGraph循环（图绕圈！）")
    print("=" * 50)

    # 1. 创建图
    graph = StateGraph(State)

    # 2. 添加节点
    graph.add_node("write", write_node)   # 写作节点！
    graph.add_node("final", final_node)   # 定稿节点！

    # 3. 添加边
    graph.add_edge(START, "write")        # 开始 → 写作

    # 条件边！关键！
    # route返回"again" → 回到write节点自己！（循环！）
    # route返回"done" → 去final节点！（结束！）
    graph.add_conditional_edges(
        "write",
        route,
        {
            "again": "write",    # 🔄 指回自己！这就是循环！
            "done": "final",     # → 定稿！
        }
    )

    graph.add_edge("final", END)

    # 4. 编译
    app = graph.compile()

    print("图的结构：开始 → [写作] →(字数够? → 定稿 | 不够 → 绕回写作!)")
    print()

    # 5. 运行！
    print("【运行图】用户主题：咖啡店开业文案！")
    result = app.invoke({"topic": "咖啡店开业文案", "attempts": 0})
    print()
    print(f"最终定稿（第{result['attempts']}次写出来的，{len(result['final'])}字）：")
    print("=" * 50)
    print(result["final"])
    print("=" * 50)
    print()

    # 6. 总结
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 循环的本质：条件边的'目标'指回自己！")
    print("2. route返回'again' → 回到write节点 → 再写一遍！")
    print("3. 必须有退出条件（attempts < 5）！否则死循环！")
    print("4. 这是while循环做不到的：循环写在'图'里，看得见！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
