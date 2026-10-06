# ============================================================
# day18/langgraph_basic.py - LangGraph入门（小白级详细注释版）
#
# LangGraph是什么？
#   = LangChain公司出的"流程图"框架！用画图的方式编排AI程序！
#
# 核心概念（就4个）：
#   State（状态）：所有节点共享的一个字典！数据靠它传递！
#   Node（节点）：图里的一个"工作步骤"，本质是一个普通函数！
#   Edge（边）：规定节点之间的执行顺序！
#   compile/invoke：把"图纸"变成"机器"，再启动机器！
# ============================================================

# ① 导入工具
from typing import TypedDict
# TypedDict：Python自带的工具，用来"规定字典的形状"（有哪些键、值是什么类型）

from langgraph.graph import StateGraph, START, END
# 从langgraph库导入3样东西：
#   StateGraph：图的"构造器"（造图用的类）
#   START：特殊节点"起点"（图的入口，固定叫START）
#   END：特殊节点"终点"（图的出口，固定叫END）

# ② 定义状态（State）
class State(TypedDict):
    # 定义一个类，规定"状态字典"长什么样
    question: str   # 键"question"，值是字符串（用户的问题）
    answer: str     # 键"answer"，值是字符串（AI的答案）

# ③ 定义节点A（就是一个普通函数！）
def node_a(state: State) -> State:
    # 参数 state：当前的状态字典（图传进来的）
    # 返回值：一个"更新片段"（字典）
    question = state["question"]
    # 从状态字典里，用键"question"取出用户的问题
    # 这就叫"读状态"：state["键名"] = 取值
    print(f"  [节点A] 收到问题：{question}")
    return {"answer": f"已经处理了你的问题：{question}"}
    # 返回一个字典，只包含"我要改的字段"！
    # LangGraph会自动把它合并进共享状态！
    # 注意：没有返回question！因为question不需要改！

# ④ 定义节点B（又一个普通函数！）
def node_b(state: State) -> State:
    # 同样：接收状态字典，返回更新片段
    answer = state["answer"]
    # 从状态字典里，用键"answer"取出节点A写好的答案
    # 这就是"状态流动"：A写了answer，B能读到！
    print(f"  [节点B] 收到答案：{answer}")
    return {"answer": f"【最终答案】{answer}，处理完毕！"}
    # 覆盖answer字段！

# ⑤ 主函数：画图 + 编译 + 运行
def main():
    print("=" * 50)
    print("LangGraph入门（最简单的图！）")
    print("=" * 50)

    # ===== 第1步：创建图 =====
    graph = StateGraph(State)
    # 创建一张"图"，告诉它：状态是State这种形状！
    # 现在图是空的，还没有任何节点

    # ===== 第2步：添加节点 =====
    graph.add_node("A", node_a)
    # 把函数node_a放进图里，给它起个名字叫"A"
    # 注意！这里只是"登记"！函数现在不会执行！
    # 名字是自己起的，随便叫啥都行（"A"、"第一步"都可以）

    graph.add_node("B", node_b)
    # 把函数node_b放进图里，名字叫"B"

    # ===== 第3步：添加边（规定执行顺序）=====
    graph.add_edge(START, "A")
    # 连线：起点 → 节点A
    # 意思是：图一启动，先跑节点A

    graph.add_edge("A", "B")
    # 连线：节点A → 节点B
    # 意思是：A跑完，接着跑B

    graph.add_edge("B", END)
    # 连线：节点B → 终点
    # 意思是：B跑完，整个图结束

    # ===== 第4步：编译 =====
    app = graph.compile()
    # 把"图纸"变成"能运行的机器"！
    # 编译后返回一个app对象！只有app才能invoke！
    # （图纸不能跑，机器才能跑！）

    # ===== 第5步：运行 =====
    result = app.invoke({"question": "什么是LangGraph？"})
    # invoke = 启动机器！
    # 传入"初始状态字典"（只有question，answer还没有）
    # 图会按边的顺序自动跑：START → A → B → END
    # 跑完后，返回"最终的状态字典"（存在result里）

    # ===== 第6步：看结果 =====
    print()
    print(f"最终结果：{result['answer']}")
    # 从返回的状态字典里，取出answer键的值！

    # ===== 第7步：总结 =====
    print()
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. State：图里流动的数据！所有节点共享！")
    print("2. Node：每个节点是一个函数！接收状态！返回更新片段！")
    print("3. Edge：边！决定流程怎么走！")
    print("4. compile()：把图编译成可以运行的程序！")
    print("5. invoke()：运行图！输入初始状态！")

# ⑥ 启动入口
if __name__ == "__main__":
    # 只有直接运行这个文件时才执行main()
    main()
