# Day 18 - LangGraph多Agent协作

## 今天学了什么？

学习LangGraph（LangChain官方的多Agent编排框架），目标是把"多Agent协作"搞透，面试能答上"怎么编排多个Agent一起干活？"

---

## 今天做了什么？

1. 创建了day18文件夹
2. 写了langgraph_basic.py，LangGraph基础（节点、边、状态、编译）
3. 写了langgraph_conditional.py，条件边（分叉路由）
4. 写了langgraph_multi_agent.py，多Agent串联
5. 写了langgraph_supervisor.py，主从Agent（主管+员工）
6. 写了langgraph_human.py，人在回路（暂停等人类）
7. 写了langgraph_loop.py，循环（条件边绕回自己）
8. 写了langgraph_parallel.py，并行（分发+汇合）
9. 写了langgraph_final_demo.py，终极综合Demo（并行+循环+人在回路三合一）

---

## LangGraph核心概念

### 1. LangGraph是什么？
LangGraph是LangChain公司出的"流程图式流程编排框架"！
- LangChain管零件（提示词、模型、检索器）
- LangGraph管流程（节点怎么走、怎么分叉、怎么循环、怎么暂停）
- 对比：LangChain的链是直线（A→B→C），LangGraph的图能分叉/循环/暂停！

### 2. 三大基础零件（basic）
- State（状态）：共享字典！流程里需要传递的数据！
- Node（节点）：函数！读状态→干活→返回"更新片段"！片段自动合并进状态！
- Edge（边）：连接节点！定义顺序！
- compile()编译 → invoke()运行！

### 3. 条件边（conditional）
- add_conditional_edges(节点, 路由函数, {暗号: 目标节点})
- 路由函数返回"暗号"字符串 → LangGraph拿暗号查表 → 去对应节点！
- 条件边必须配函数！这是API设计！函数里能写任意逻辑！

### 4. 多Agent（multi_agent）
- "多Agent" = 多个角色化节点！每个节点调一次大模型！
- 前一个节点的输出写进State！后一个节点读取消费！
- State字段完全自己定义！按"流程需要传递的数据"设计！

### 5. 主从Agent（supervisor）
- 主管节点：用大模型判断任务类型！（不是关键词！大模型理解语义！）
- 路由函数：纯传话！读task_type返回暗号！
- 员工节点：writer/coder/analyst！各调大模型、不同角色提示词！
- 判断的活交给大模型！指路的活交给route！干活的活交给员工！
- 大模型输出不可靠！必须清理（strip/lower）+模糊匹配+else兜底！

### 6. 人在回路（human）
- interrupt()：图暂停！把信息包（字典）抛给人类！
- checkpointer（MemorySaver）：记住暂停在哪！必须！否则报错！
- thread_id：会话编号！图靠它记住"这是哪次对话"！
- Command(resume=人类输入)：带人类答案从暂停处继续！
- 真正等人类输入的是input()！interrupt只是"暂停+抛信息"！

### 7. 循环（loop）
- 循环的本质：条件边的"目标"指回自己！（"again": "write"）
- 必须有退出条件（次数/字数上限）！否则死循环！
- 图里的循环看得见！还能和分叉、暂停自由组合！

### 8. 并行（parallel）
- 分发（fan-out）：START分叉到多个节点 → 同时跑！
- 汇合（fan-in）：多个节点都指向一个节点 → 自动等齐！
- 总耗时≈单个耗时！省时间！
- 实测：3个研究员各3秒，并行3秒，串行9秒！

### 9. 终极综合Demo（final_demo）
- 并行+循环+人在回路三合一！
- 3研究员并行研究 → 主编汇总 → 人类审核 → 不满意绕回主编重写（最多3轮）→ 定稿！
- 绕回的是"主编"不是START！并行报告还在状态里！不重跑！
- 状态字段是组合的粘合剂：报告/attempts轮数/human_feedback意见！

---

## 今天学到了什么关键点？

### 1. LangGraph只标准化"机制"，不标准化"业务"！
节点怎么定义、边怎么连、状态怎么合并——机制是固定的！
State放什么字段、节点干什么活——100%自己定！
State字段 = 流程里需要传递哪些数据！5~20个字段常见！

### 2. 条件边必须配函数！
API设计！不能直接"按字段路由"！
函数能装任何逻辑（读多字段、组合判断、调别的函数）！

### 3. 大模型输出不可靠！必须兜底！
主管让模型返回"writer"，它可能返回"Writer。"或解释一大堆！
必须：strip().lower()清理 → 模糊匹配 → else兜底！
这是AI工程铁律！

### 4. human必须三件套！
checkpointer + thread_id + Command(resume=...)
缺一个都报错或无法恢复！

### 5. 循环必须有退出条件！
条件边绕回自己 = 循环！
没有"次数上限"判断 = 死循环卡死！

### 6. 并行自动等齐！
多个边指向一个节点 → LangGraph自动等所有上游完成！
不用写任何等待代码！

---

## 今天遇到了什么问题？

### 1. Windows下print输出被缓冲吞掉！
直接管道运行时，循环/并行的print输出丢失！
解决：重定向到文件再读取（python -u + > output.txt）！

### 2. human不带checkpointer报错！
RuntimeError: Cannot use Command(resume=...) without checkpointer
解决：graph.compile(checkpointer=MemorySaver())！

### 3. 大模型"不听话"！
主管让它只返回一个词，它可能输出一大段！
解决：清理+模糊匹配+else兜底！

### 4. 并行demo第一次没"转起来"！
循环demo第一次写出来就达标，没展示循环！
解决：加"第1遍强制重写"，保证看到循环！

---

## 一句话总结

> **今天学了LangGraph！用图编排多Agent：节点干活、边定顺序、条件边分叉、循环绕圈、并行分发汇合、interrupt暂停等人类！LangChain管零件，LangGraph管流程！八九十（子图/持久化/流式）等实战需要时再学！**

---

## 明天学什么？

Day 19！向量数据库深入（FAISS vs Milvus vs Pinecone）！
