# -*- coding: utf-8 -*-
"""
Day 21 - 评测Agent效果！（三合一评测demo！）

评测三件事（面试必答！）：
① 对话质量（LLM当裁判打分！）
② 工具调用准确率（function calling！看模型选对工具没！）
③ RAG检索命中率（标准答案在不在检索结果里！）

全部用免费API：智谱glm-4-flash（对话/裁判）+ 硅基BGE-M3（向量）！
"""

import os
import re
import math
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(r"D:\AGENTMAKER\ai-learning\day18\.env")

chat_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)


# ============ ① 对话质量评测（LLM当裁判！） ============
def eval_dialogue():
    print("=" * 60)
    print("【① 对话质量评测】（被测LLM回答 → 裁判LLM打分！）")
    cases = [
        {"question": "CPI太高对股市有什么影响？", "expect": "包含加息/通胀/下跌等相关内容"},
        {"question": "什么是RAG？", "expect": "包含检索/生成/知识库等相关内容"},
        {"question": "3+5等于几？", "expect": "等于8"},
    ]
    total, good = 0, 0
    for case in cases:
        total += 1
        # 被测Agent回答（就是智谱！）
        resp = chat_client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": case["question"]}]
        )
        answer = resp.choices[0].message.content
        # 裁判LLM打分（大模型当裁判！评测圈常用！）
        judge = chat_client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": "你是评测裁判！根据期望要点给回答打分（0-10分），只输出分数和一句话理由。"},
                {"role": "user", "content": f"问题：{case['question']}\n期望：{case['expect']}\n回答：{answer}"}
            ]
        )
        score_text = judge.choices[0].message.content
        # 提取分数
        m = re.search(r"(\d+(?:\.\d+)?)", score_text)
        score = float(m.group(1)) if m else 0
        if score >= 7:
            good += 1
        print(f"\nQ: {case['question']}")
        print(f"A: {answer[:60]}...")
        print(f"裁判: {score_text[:80]}")
    print(f"\n✅ 对话质量：{good}/{total} 达标（≥7分）")


# ============ ② 工具调用准确率评测（function calling！） ============
def eval_tools():
    print("\n" + "=" * 60)
    print("【② 工具调用准确率评测】（模型自己选工具！看选对没！）")
    tools = [
        {"type": "function", "function": {
            "name": "get_weather", "description": "查询天气",
            "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "城市名"}}, "required": ["city"]}}},
        {"type": "function", "function": {
            "name": "get_exchange_rate", "description": "查询汇率",
            "parameters": {"type": "object", "properties": {"currency": {"type": "string", "description": "货币代码"}}, "required": ["currency"]}}},
        {"type": "function", "function": {
            "name": "search_news", "description": "搜索新闻",
            "parameters": {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}}},
    ]
    cases = [
        {"q": "北京明天天气怎么样？", "expect": "get_weather"},
        {"q": "美元兑人民币汇率是多少？", "expect": "get_exchange_rate"},
        {"q": "帮我搜一下最近的AI新闻", "expect": "search_news"},
        {"q": "你好", "expect": None},  # 闲聊不该调工具！
    ]
    total, correct = 0, 0
    for case in cases:
        total += 1
        resp = chat_client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": case["q"]}],
            tools=tools,
        )
        msg = resp.choices[0].message
        called = msg.tool_calls[0].function.name if msg.tool_calls else None
        ok = called == case["expect"]
        if ok:
            correct += 1
        print(f"\nQ: {case['q']}")
        print(f"模型选了: {called} | 期望: {case['expect']} | {'✅' if ok else '❌'}")
    print(f"\n✅ 工具调用准确率: {correct}/{total}")


# ============ ③ RAG检索命中率评测 ============
def eval_rag():
    print("\n" + "=" * 60)
    print("【③ RAG检索命中率评测】（标准答案在不在检索结果里！）")
    # 知识库：CPI文档！（day08！）
    with open(r"D:\AGENTMAKER\ai-learning\day08\CPI基础知识.txt", "r", encoding="utf-8") as f:
        text = f.read()
    chunks = [text[i:i + 200] for i in range(0, len(text), 200) if text[i:i + 200].strip()]
    # 预embedding！
    vecs = embed_client.embeddings.create(model="BAAI/bge-m3", input=chunks)
    chunk_vecs = [v.embedding for v in vecs.data]

    def cos(a, b):
        return sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) + 1e-9)

    # 评测问题（每个问题对应"标准片段"里的关键词！）
    cases = [
        {"q": "CPI是什么？", "keyword": "CPI是居民消费价格指数"},
        {"q": "CPI太高会怎样？", "keyword": "通货膨胀"},
        {"q": "CPI太低会怎样？", "keyword": "通货紧缩"},
    ]
    total, hit = 0, 0
    for case in cases:
        total += 1
        qv = embed_client.embeddings.create(model="BAAI/bge-m3", input=[case["q"]]).data[0].embedding
        scored = sorted(zip(chunks, chunk_vecs), key=lambda x: -cos(qv, x[1]))[:3]
        found = any(case["keyword"] in c for c, _ in scored)
        if found:
            hit += 1
        print(f"\nQ: {case['q']} | 命中标准片段: {'✅' if found else '❌'}")
    print(f"\n✅ RAG命中率: {hit}/{total}")


eval_dialogue()
eval_tools()
eval_rag()
print("\n" + "=" * 60)
print("🎯 Day 21 三合一评测完成！")
