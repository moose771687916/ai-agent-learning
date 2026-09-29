# Day 15 - 深入学习LangChain

## 今天学了什么？

深入学习LangChain框架，目标是把LangChain核心组件学透，为面试做准备。

---

## 今天做了什么？

1. 创建了day15文件夹
2. 写了langchain_demo.py，最简单的Chain（prompt | llm | output_parser）
3. 写了langchain_agent.py，带工具的Agent，自己写工具调用循环
4. 写了langchain_rag.py，用LangChain写RAG
5. 写了langchain_full_agent.py，完整版（RAG + 工具）
6. 自己创建了向量库（create_vector_store.py）
7. 成功测试了完整版Agent：既有RAG，又有工具！

---

## LangChain核心概念

### 1. Chain是什么？
Chain就是流水线！用户输入会自动传给每一步！

### 2. |竖线是什么意思？
就是流水线传送带！A的输出传给B！B的输出传给C！

### 3. RAG是什么？
RAG就是先从向量库里找相关文档！然后把文档和问题一起给大模型！大模型根据文档回答！

### 4. Agent是什么？
Agent就是大模型可以自己决定要不要调用工具！

### 5. 完整版Agent是什么？
既有RAG，又有工具！大模型可以查知识库，也可以用工具！

---

## 今天遇到了什么问题？

### 1. 硅基流动余额不足！
bge-m3的免费额度用完了！然后换了新的密钥！

### 2. 向量库不匹配！
不同的embedding模型，向量维度不一样！不能混用！

### 3. 知识库里面没有相关内容！
retriever永远会返回4个文档！哪怕跟问题一点关系都没有！然后大模型自己判断有没有关系！

---

## 一句话总结

> **今天学了LangChain！Chain、RAG、Agent！还有完整版Agent！既有RAG，又有工具！**

---

## 明天学什么？

Day 16！继续学LangChain！
