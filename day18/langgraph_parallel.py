# ============================================================
# day18/langgraph_parallel.py - LangGraph并行（多Agent同时干活！）
#
# 新能力：多个节点从START分叉 → 同时跑 → 汇合到一个节点！
#         fan-out（分发）+ fan-in（汇合）！
# 场景：写报告！3个研究员【同时】研究3个方面，最后主编汇总！
# 效果：并行耗时 ≈ 单个耗时！串行耗时 = 3倍！
# ============================================================

from typing import TypedDict
import time
from langgraph.graph import StateGraph, START, END

# ============================================================
# 1. 定义状态
# ============================================================

class State(TypedDict):
    """状态"""
    topic: str            # 报告主题
    market_report: str    # 市场报告（研究员1的产出）
    tech_report: str      # 技术报告（研究员2的产出）
    policy_report: str    # 政策报告（研究员3的产出）
    final: str            # 主编汇总的最终报告


# ============================================================
# 2. 三个研究员节点！（各自独立！谁也不等谁！）
# ============================================================

def market_agent(state: State) -> State:
    """研究员1：研究市场！"""
    start = time.time()
    print(f"  [市场研究员] 开始研究！时间：{time.strftime('%H:%M:%S')}")
    
    # 模拟研究耗时3秒！（真实项目里这里是调大模型/查数据库！）
    time.sleep(3)
    
    report = f"【市场篇】{state['topic']}的市场规模持续扩大，增速达25%，竞争加剧..."
    print(f"  [市场研究员] 研究完成！耗时{time.time()-start:.1f}秒！时间：{time.strftime('%H:%M:%S')}")
    return {"market_report": report}


def tech_agent(state: State) -> State:
    """研究员2：研究技术！"""
    start = time.time()
    print(f"  [技术研究员] 开始研究！时间：{time.strftime('%H:%M:%S')}")
    
    time.sleep(3)
    
    report = f"【技术篇】{state['topic']}的电池技术突破明显，续航提升30%，智能驾驶成熟..."
    print(f"  [技术研究员] 研究完成！耗时{time.time()-start:.1f}秒！时间：{time.strftime('%H:%M:%S')}")
    return {"tech_report": report}


def policy_agent(state: State) -> State:
    """研究员3：研究政策！"""
    start = time.time()
    print(f"  [政策研究员] 开始研究！时间：{time.strftime('%H:%M:%S')}")
    
    time.sleep(3)
    
    report = f"【政策篇】{state['topic']}的补贴政策持续加码，充电桩建设提速，标准趋严..."
    print(f"  [政策研究员] 研究完成！耗时{time.time()-start:.1f}秒！时间：{time.strftime('%H:%M:%S')}")
    return {"policy_report": report}


# ============================================================
# 3. 主编节点！等3份报告都到齐了才运行！
# ============================================================

def merge_agent(state: State) -> State:
    """主编：汇总三份报告！"""
    start = time.time()
    print()
    print(f"  [主编] 三份报告都到齐了！开始汇总！时间：{time.strftime('%H:%M:%S')}")
    
    # 从状态里取出三份报告！
    combined = "\n\n".join([
        state["market_report"],
        state["tech_report"],
        state["policy_report"]
    ])
    
    # 模拟汇总耗时1秒！
    time.sleep(1)
    
    print(f"  [主编] 汇总完成！耗时{time.time()-start:.1f}秒！")
    return {"final": f"【总报告：{state['topic']}】\n\n{combined}"}


# ============================================================
# 4. 画图！关键：START分叉到3个节点！再汇合到merge！
# ============================================================

def main():
    print("=" * 50)
    print("LangGraph并行（多Agent同时干活！）")
    print("=" * 50)

    # 1. 创建图
    graph = StateGraph(State)

    # 2. 添加节点
    graph.add_node("market", market_agent)   # 市场研究员
    graph.add_node("tech", tech_agent)       # 技术研究员
    graph.add_node("policy", policy_agent)   # 政策研究员
    graph.add_node("merge", merge_agent)     # 主编（汇总）

    # 3. 添加边！
    # 分发（fan-out）：START同时分到3个研究员！（并行！）
    graph.add_edge(START, "market")
    graph.add_edge(START, "tech")
    graph.add_edge(START, "policy")
    
    # 汇合（fan-in）：3个研究员都完成后 → 到主编！（等齐才跑！）
    graph.add_edge("market", "merge")
    graph.add_edge("tech", "merge")
    graph.add_edge("policy", "merge")
    
    graph.add_edge("merge", END)

    # 4. 编译
    app = graph.compile()

    print("图的结构：")
    print("            ┌→ [市场研究员] ─┐")
    print("  START ──→ ├→ [技术研究员] ─┼→ [主编汇总] → END")
    print("            └→ [政策研究员] ─┘")
    print("  3个研究员【同时】跑！主编等他们都完成再汇总！")
    print()

    # 5. 运行！计时！
    print("【运行图】用户主题：新能源汽车行业报告！")
    print()

    total_start = time.time()
    result = app.invoke({"topic": "新能源汽车"})
    total_cost = time.time() - total_start

    print()
    print(f"🎯 总耗时：{total_cost:.1f}秒！")
    print(f"   （如果串行：3个研究员各3秒 = 9秒！并行只要3秒多！）")
    print()
    print("=" * 50)
    print("最终报告：")
    print("=" * 50)
    print(result["final"])
    print("=" * 50)
    print()

    # 6. 总结
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 分发（fan-out）：START分叉到多个节点 → 并行跑！")
    print("2. 汇合（fan-in）：多个节点都完成后 → 汇到下一个节点！")
    print("3. 并行 = 总耗时≈单个耗时！省时间！")
    print("4. 汇合节点自动等所有上游完成！不用自己管！")
    print("5. 真实项目：每个研究员里是调大模型/查数据库！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
