# ============================================================
# day18/langgraph_final_demo.py - Day18 终极综合Demo！
# 并行 + 循环 + 人在回路 三合一！
#
# 场景：写"新能源汽车行业报告"！
#   ① 3个研究员【并行】研究：市场/技术/政策！
#   ② 主编汇总！
#   ③ 人类审核⛔！
#   ④ 不满意 → 🔄绕回主编重写（最多3轮）！满意 → 定稿！
# ============================================================

from typing import TypedDict
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

load_dotenv()

# ============================================================
# 1. 状态
# ============================================================

class State(TypedDict):
    """状态"""
    topic: str              # 报告主题
    market_report: str      # 市场报告（并行1）
    tech_report: str        # 技术报告（并行2）
    policy_report: str      # 政策报告（并行3）
    draft: str              # 主编汇总的草稿
    attempts: int           # 重写轮数！
    human_feedback: str     # 人类意见
    final: str              # 最终定稿


# ============================================================
# 2. 大模型客户端
# ============================================================

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

def call_model(system_prompt: str, user_content: str) -> str:
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    )
    return response.choices[0].message.content


# ============================================================
# 3. 三个研究员（并行！）
# ============================================================

def market_agent(state: State) -> State:
    start = time.time()
    print(f"  [市场研究员] 开始！时间：{time.strftime('%H:%M:%S')}")
    time.sleep(3)   # 模拟研究耗时！
    report = f"【市场篇】{state['topic']}市场规模2026年预计达8000亿，增速25%，比亚迪/特斯拉领跑，竞争加剧..."
    print(f"  [市场研究员] 完成！耗时{time.time()-start:.1f}秒！")
    return {"market_report": report}


def tech_agent(state: State) -> State:
    start = time.time()
    print(f"  [技术研究员] 开始！时间：{time.strftime('%H:%M:%S')}")
    time.sleep(3)
    report = f"【技术篇】{state['topic']}电池能量密度突破400Wh/kg，800V快充普及，智能驾驶L3落地..."
    print(f"  [技术研究员] 完成！耗时{time.time()-start:.1f}秒！")
    return {"tech_report": report}


def policy_agent(state: State) -> State:
    start = time.time()
    print(f"  [政策研究员] 开始！时间：{time.strftime('%H:%M:%S')}")
    time.sleep(3)
    report = f"【政策篇】{state['topic']}购置税减免延续，充电桩建设提速，碳积分政策趋严，出口壁垒增加..."
    print(f"  [政策研究员] 完成！耗时{time.time()-start:.1f}秒！")
    return {"policy_report": report}


# ============================================================
# 4. 主编（汇总！也是循环的"重写点"！）
# ============================================================

def editor_agent(state: State) -> State:
    attempts = state["attempts"] + 1
    print(f"  [主编] 第{attempts}轮汇总！")
    
    combined = "\n\n".join([
        state["market_report"],
        state["tech_report"],
        state["policy_report"]
    ])
    
    # 如果有人类修改意见 → 让大模型按意见改！
    feedback = state.get("human_feedback")
    if feedback:
        print(f"  [主编] 按人类意见修改中：{feedback}")
        draft = call_model(
            "你是一个主编！请根据修改意见，把报告改得更好！",
            f"原始报告：\n{combined}\n\n修改意见：{feedback}"
        )
    else:
        print(f"  [主编] 第一次汇总！")
        draft = call_model(
            "你是一个主编！请把三份报告汇总成一篇完整的行业报告！",
            combined
        )
    
    return {"draft": draft, "attempts": attempts}


# ============================================================
# 5. 人类审核（暂停！）
# ============================================================

def human_check(state: State) -> State:
    print(f"  [人类审核] ⛔ 暂停！等人类审核！")
    human_input = interrupt({
        "message": "请审核报告！输入OK通过！或输入修改意见！",
        "draft": state["draft"]
    })
    print(f"  [人类审核] 人类输入了：{human_input}")
    return {"human_feedback": human_input}


# ============================================================
# 6. 路由！循环的"出口判断"！
# ============================================================

def route(state: State) -> str:
    feedback = state["human_feedback"]
    attempts = state["attempts"]
    
    # 通过 → 定稿！
    if "OK" in feedback or "通过" in feedback:
        print(f"  [路由] 人类通过了！定稿！")
        return "approve"
    
    # 不通过 且 没写满3轮 → 绕回主编！（循环！）
    if attempts < 3:
        print(f"  [路由] 人类不满意！第{attempts}轮！绕回主编重写！")
        return "revise"
    
    # 不通过 且 写满3轮 → 强制定稿！（退出条件！）
    print(f"  [路由] 已重写3轮！强制定稿！")
    return "approve"


def final_agent(state: State) -> State:
    print(f"  [定稿] 最终定稿！")
    return {"final": f"【最终报告（第{state['attempts']}轮）】\n{state['draft']}"}


# ============================================================
# 7. 画图！并行 + 循环 + human 三合一！
# ============================================================

def main():
    print("=" * 60)
    print("Day18 终极综合Demo：并行 + 循环 + 人在回路！")
    print("=" * 60)

    graph = StateGraph(State)

    # 节点
    graph.add_node("market", market_agent)
    graph.add_node("tech", tech_agent)
    graph.add_node("policy", policy_agent)
    graph.add_node("editor", editor_agent)   # 主编（汇总/重写点！）
    graph.add_node("human", human_check)     # 人类审核（暂停点！）
    graph.add_node("final", final_agent)     # 定稿

    # 边：并行分发！
    graph.add_edge(START, "market")
    graph.add_edge(START, "tech")
    graph.add_edge(START, "policy")
    
    # 边：并行汇合 → 主编！
    graph.add_edge("market", "editor")
    graph.add_edge("tech", "editor")
    graph.add_edge("policy", "editor")
    
    # 边：主编 → 人类审核！
    graph.add_edge("editor", "human")
    
    # 边：条件边！循环的关键！
    graph.add_conditional_edges(
        "human",
        route,
        {
            "approve": "final",   # 通过 → 定稿！
            "revise": "editor",   # 🔄 不满意 → 绕回主编！（循环！）
        }
    )
    
    graph.add_edge("final", END)

    # 编译！必须带checkpointer！（human需要！）
    checkpointer = MemorySaver()
    app = graph.compile(checkpointer=checkpointer)

    print("图的结构：")
    print("            ┌→ [市场研究员] ─┐")
    print("  START ──→ ├→ [技术研究员] ─┼→ [主编] → [人类审核⛔] → 通过? → 定稿 → END")
    print("            └→ [政策研究员] ─┘              ↑           └ 不满意 → 🔄绕回主编！")
    print()
    print("  = 并行（3研究员同时） + 循环（不满意重写） + 人在回路（人类审核）")
    print()

    # 会话配置（human需要thread_id！）
    config = {"configurable": {"thread_id": "final-demo-1"}}

    total_start = time.time()

    # ===== 第一次运行：跑到human暂停！ =====
    print("【第1轮】用户：写一篇新能源汽车行业报告！")
    result = app.invoke({"topic": "新能源汽车", "attempts": 0}, config)
    print()
    print(f"  ⛔ 图暂停了！草稿（第{result['draft'][:0] or '1'}轮）等待审核...")
    print(f"  ⛔ 草稿摘要：{result['__interrupt__'][0].value['draft'][:80]}...")
    print()

    # ===== 人类第1次审核：不满意！触发循环！ =====
    print("【人类第1次审核】输入：太短了！再写详细一点！")
    # 带着人类意见继续跑！→ human_check返回意见 → route判断"revise" → 绕回主编重写！
    # → 主编重写完成 → 又跑到human暂停！这次的返回值就是新的暂停信息！
    result2 = app.invoke(Command(resume="太短了！再写详细一点！"), config)
    print()
    print("  🔄 人类不满意！已绕回主编重写！")
    print()

    # ===== 主编重写后：再次跑到human暂停！ =====
    print("【第2轮】主编重写完成，图再次暂停等人类审核！")
    print(f"  ⛔ 草稿摘要：{result2['__interrupt__'][0].value['draft'][:80]}...")
    print()

    # ===== 人类第2次审核：通过！ =====
    print("【人类第2次审核】输入：OK，通过！")
    result3 = app.invoke(Command(resume="OK，通过！"), config)

    total_cost = time.time() - total_start

    print()
    print(f"🎯 总耗时：{total_cost:.1f}秒！（含3个研究员并行3秒 + 2轮主编大模型）")
    print()
    print("=" * 60)
    print("最终报告：")
    print("=" * 60)
    print(result3["final"])
    print("=" * 60)
    print()

    print("=" * 60)
    print("总结：")
    print("=" * 60)
    print("1. 并行：3个研究员同时跑！总耗时≈单个耗时！")
    print("2. 循环：人类不满意 → 条件边绕回主编 → 重写！（最多3轮）")
    print("3. 人在回路：human暂停等人类！resume继续！")
    print("4. 三者可以自由组合！这就是LangGraph的威力！")
    print("5. 注意：循环和human都要求'状态字段'记录进度（attempts/feedback）！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
