# ============================================================
# day18/langgraph_human.py - 人在回路（Human-in-the-loop）！
# 图跑着跑着！停下来！等人类确认！
# ============================================================

from typing import TypedDict
from dotenv import load_dotenv
import os
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# ============================================================
# 1. 定义状态
# ============================================================

class State(TypedDict):
    """状态"""
    question: str        # 用户的需求
    draft: str           # AI写的草稿
    human_feedback: str  # 人类的审核意见
    final: str           # 最终定稿


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
# 3. 节点们！
# ============================================================

def draft_agent(state: State) -> State:
    """AI写草稿！"""
    question = state["question"]
    print(f"  [草稿Agent] 正在写草稿...")
    draft = call_model(
        "你是一个文案写手！请写一段开业宣传文案！生动有趣！",
        question
    )
    print(f"  [草稿Agent] 草稿写好了！")
    return {"draft": draft}


def human_check(state: State) -> State:
    """人在回路！暂停！等人类确认！"""
    print(f"  [人类确认节点] ⛔ 暂停！等人类审核！")
    
    # interrupt()：图在这里暂停！把问题抛给人类！
    # 人类输入的内容！会作为返回值！存到human_input！
    human_input = interrupt({
        "message": "请审核草稿！输入OK通过！或输入修改意见！",
        "draft": state["draft"]
    })
    
    print(f"  [人类确认节点] 人类输入了：{human_input}")
    # 把人类的意见存到状态里！给后面的节点用！
    return {"human_feedback": human_input}


def final_agent(state: State) -> State:
    """定稿！根据人类意见处理！"""
    draft = state["draft"]
    feedback = state["human_feedback"]
    
    # 如果人类说OK/通过 → 直接定稿！
    if "OK" in feedback or "通过" in feedback:
        print(f"  [定稿Agent] 人类通过了！直接定稿！")
        return {"final": f"【最终定稿】\n{draft}"}
    
    # 否则！人类给了修改意见！让大模型根据意见修改！
    print(f"  [定稿Agent] 人类给了修改意见：{feedback}")
    print(f"  [定稿Agent] 正在根据意见修改草稿...")
    revised = call_model(
        "你是一个文案写手！请根据人类的修改意见，修改下面的草稿！保留原文优点！",
        f"草稿：\n{draft}\n\n修改意见：{feedback}"
    )
    return {"final": f"【按人类意见修改后的定稿】\n{revised}"}


# ============================================================
# 4. 画图！
# ============================================================

def main():
    print("=" * 50)
    print("人在回路（Human-in-the-loop）")
    print("=" * 50)
    
    # 1. 创建图！
    graph = StateGraph(State)
    
    # 2. 添加节点！
    graph.add_node("draft", draft_agent)     # 写草稿！
    graph.add_node("human", human_check)     # 人类确认！（暂停点！）
    graph.add_node("final", final_agent)     # 定稿！
    
    # 3. 添加边！
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "human")
    graph.add_edge("human", "final")
    graph.add_edge("final", END)
    
    # 4. 编译！
    # checkpointer（检查点）：记住图暂停在哪！有了它，才能resume继续！
    checkpointer = MemorySaver()
    app = graph.compile(checkpointer=checkpointer)
    
    print("图的结构：开始 → [草稿Agent] → [人类确认⛔] → [定稿Agent] → 结束")
    print()
    
    # ==========================================
    # 5. 第一次运行！图会停在【人类确认】节点！
    # ==========================================
    print("【第一次运行】用户：帮我写一段奶茶店的开业文案！")
    
    # thread_id：给这个对话一个编号！LangGraph靠它记住暂停在哪！
    config = {"configurable": {"thread_id": "thread-demo-1"}}
    
    result = app.invoke({"question": "帮我写一段奶茶店的开业文案！"}, config)
    
    print()
    print(f"  ⛔ 图暂停了！等待人类审核！")
    print(f"  ⛔ 暂停信息：{result['__interrupt__'][0].value['message']}")
    print(f"  ⛔ AI写的草稿：")
    print(f"     {result['__interrupt__'][0].value['draft']}")
    print()
    
    # ==========================================
    # 6. 人类审核！【真的人！程序停下来等输入！】
    # ==========================================
    print("【人类审核中...】")
    print("  ⛔ 程序停在这里！等你真正输入！")
    print()
    
    # input()：程序真正停下来！等人类在终端打字！
    human_input = input("  请审核草稿！输入OK通过！或输入修改意见！\n  > ")
    
    print()
    print(f"  ✅ 你输入了：{human_input}")
    print()
    
    # ==========================================
    # 7. 第二次运行！把你输入的传回去！继续！
    # ==========================================
    print("【第二次运行】（人类已确认）")
    
    # Command(resume=你真正输入的！)：图继续跑！
    result2 = app.invoke(Command(resume=human_input), config)
    
    print()
    print("  ✅ 图继续跑了！最终结果：")
    print(result2["final"])
    print()
    
    # 8. 总结！
    print("=" * 50)
    print("总结：")
    print("=" * 50)
    print("1. interrupt()：图暂停！把问题抛给人类！")
    print("2. thread_id：记住暂停在哪！")
    print("3. Command(resume=...)：把人类输入传回去！图继续跑！")
    print("4. 人在回路：AI干活！关键时刻人类把关！")
    print("5. 企业场景：AI写邮件→人类确认→才发送！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
