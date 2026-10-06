# ============================================================
# day18/langgraph_supervisor.py - 主从Agent！
# 主管Agent分配任务！员工Agent干活！
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
    question: str      # 用户的问题
    task_type: str     # 主管判断的任务类型：writer/coder/analyst
    answer: str        # 员工的回答


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
# 3. 主管Agent！用大模型判断任务类型！
# ============================================================

def supervisor_node(state: State) -> State:
    """主管Agent：看问题！判断派给谁！"""
    question = state["question"]
    print(f"  [主管Agent] 收到问题：{question}")
    print(f"  [主管Agent] 正在判断任务类型...")
    
    # 让大模型判断！只返回一个词！
    result = call_model(
        "你是一个任务分配主管！请判断下面这个用户请求属于哪种任务：\n"
        "1. 写文案/写文章/写诗 → 返回：writer\n"
        "2. 写代码/写程序/实现功能 → 返回：coder\n"
        "3. 数据分析/算数/统计 → 返回：analyst\n"
        "只返回一个单词！不要解释！不要加标点！",
        f"用户请求：{question}"
    )
    
    # 清理结果！
    task_type = result.strip().lower()
    # 如果大模型输出不标准！兜底判断！
    if "writer" in task_type:
        task_type = "writer"
    elif "coder" in task_type:
        task_type = "coder"
    else:
        task_type = "analyst"
    
    print(f"  [主管Agent] 判断结果：{task_type}")
    return {"task_type": task_type}


# ============================================================
# 4. 路由函数！根据主管的判断，决定去哪个员工！
# ============================================================

def route(state: State) -> str:
    """路由：主管说去谁那就去谁那！"""
    task_type = state["task_type"]
    print(f"  [路由] 主管指令：去{task_type}那里！")
    return task_type


# ============================================================
# 5. 员工Agent们！
# ============================================================

def writer_agent(state: State) -> State:
    """员工1：写手Agent！"""
    question = state["question"]
    print(f"  [写手Agent] 收到任务！开始写文案...")
    answer = call_model(
        "你是一个金牌文案写手！请写一段精彩的文案！生动有趣！",
        f"写文案的要求：{question}"
    )
    return {"answer": answer}


def coder_agent(state: State) -> State:
    """员工2：程序员Agent！"""
    question = state["question"]
    print(f"  [程序员Agent] 收到任务！开始写代码...")
    answer = call_model(
        "你是一个资深程序员！请写出完整可运行的Python代码！要有注释！",
        f"写代码的要求：{question}"
    )
    return {"answer": answer}


def analyst_agent(state: State) -> State:
    """员工3：分析师Agent！"""
    question = state["question"]
    print(f"  [分析师Agent] 收到任务！开始分析数据...")
    answer = call_model(
        "你是一个数据分析师！请清晰地分析数据！给出结论！",
        f"数据分析的要求：{question}"
    )
    return {"answer": answer}


# ============================================================
# 6. 画图！
# ============================================================

def main():
    print("=" * 50)
    print("主从Agent（主管分配任务！）")
    print("=" * 50)
    
    # 1. 创建图！
    graph = StateGraph(State)
    
    # 2. 添加节点！
    graph.add_node("supervisor", supervisor_node)  # 主管Agent！
    graph.add_node("writer", writer_agent)         # 写手Agent！
    graph.add_node("coder", coder_agent)           # 程序员Agent！
    graph.add_node("analyst", analyst_agent)       # 分析师Agent！
    
    # 3. 添加边！
    graph.add_edge(START, "supervisor")   # 开始 → 主管！
    # 条件边！主管判断后，派给对应的员工！
    graph.add_conditional_edges(
        "supervisor",
        route,
        {
            "writer": "writer",    # → 写手！
            "coder": "coder",      # → 程序员！
            "analyst": "analyst",  # → 分析师！
        }
    )
    graph.add_edge("writer", END)
    graph.add_edge("coder", END)
    graph.add_edge("analyst", END)
    
    # 4. 编译！
    app = graph.compile()
    
    print("图的结构：开始 → [主管Agent] → (writer? → 写手 | coder? → 程序员 | analyst? → 分析师) → 结束")
    print()
    
    # 5. 测试1：写文案！
    print("【测试1】用户：帮我写一段咖啡店的开业宣传文案！")
    result1 = app.invoke({"question": "帮我写一段咖啡店的开业宣传文案！"})
    print(f"  结果：{result1['answer'][:100]}...")
    print()
    
    # 6. 测试2：写代码！
    print("【测试2】用户：用Python写一个计算圆面积的函数！")
    result2 = app.invoke({"question": "用Python写一个计算圆面积的函数！"})
    print(f"  结果：{result2['answer'][:100]}...")
    print()
    
    # 7. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. 主管Agent：用大模型判断任务类型！")
    print("2. 路由函数：根据主管判断，派给对应员工！")
    print("3. 员工Agent：每个只干自己的活！")
    print("4. 主从模式：企业最常用的多Agent模式！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
