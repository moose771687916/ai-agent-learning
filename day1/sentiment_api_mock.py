# -*- coding: utf-8 -*-
"""
情感分析接口（模拟版）—— 第⑤步 FastAPI 学习
=================================================

【这个文件是干什么的】
把"情感分析"功能变成一个网址接口。别人（或者别的程序）通过
网址 POST 一句话进来，我们返回 JSON 格式的情感分析结果。

【为什么先用模拟版】
调用真正的 AI（DeepSeek/豆包）需要 API Key。但学习 FastAPI
的核心是"把函数变成网址"这件事本身，跟调不调 AI 没关系。
所以先用关键词规则模拟情感分析，把接口流程跑通，一分钱不花。
以后拿到 API Key，只需要替换 analyze_sentiment_mock 函数内部，
接口部分一行都不用改。

【怎么运行】
在命令行（这个文件所在目录）执行：
    uvicorn sentiment_api_mock:app --reload
然后浏览器打开 http://127.0.0.1:8000/docs 测试
"""

# ===== 1. 导入 FastAPI 框架 =====
# FastAPI 是"接口框架"：提供装饰器 @app.post 等工具，把普通函数变成网址接口
from fastapi import FastAPI

# pydantic 的 BaseModel：用来定义"请求的数据格式"
# FastAPI 会自动校验——别人传错格式，直接报错，不用自己写判断
from pydantic import BaseModel

# ===== 2. 创建应用实例 =====
# app 是"接口服务器"本身，uvicorn 启动时会加载这个变量
# title 只是给它起个名字，会在 /docs 文档页显示
app = FastAPI(title="情感分析接口（模拟版）")


# ===== 3. 定义请求的数据格式 =====
# 别人调用接口时，必须传一个 JSON 数据，里面必须有一个 text 字段
# 这个类就是"收件单的格式模板"：规定收件单上必须写什么
class SentimentRequest(BaseModel):
    text: str  # text 必须是字符串，比如 "今天面试通过了，太开心了！"


# ===== 4. 情感分析核心函数（先模拟，不调真实 AI） =====
# 这是"内部师傅"：以后换成真实 AI 调用，只改这个函数
def analyze_sentiment_mock(text: str):
    # 关键词词典：模拟"AI"看到这些词会怎么判断
    positive_words = ["开心", "太棒", "通过", "喜欢", "棒", "好"]   # 正面词
    negative_words = ["气死", "烂", "差", "烦", "讨厌", "失望"]     # 负面词

    # 在句子中查找命中了哪些词
    # 列表推导式：遍历词典，把出现在 text 里的词收集起来
    hit_pos = [w for w in positive_words if w in text]
    hit_neg = [w for w in negative_words if w in text]

    # 命中正面词 → 判断为正面情绪
    if hit_pos:
        return {"sentiment": "positive", "confidence": 0.9, "keywords": hit_pos}
    # 命中负面词 → 判断为负面情绪
    elif hit_neg:
        return {"sentiment": "negative", "confidence": 0.9, "keywords": hit_neg}
    # 都没命中 → 中性
    else:
        return {"sentiment": "neutral", "confidence": 0.6, "keywords": []}

    # 注意：这个返回结构（sentiment/confidence/keywords）要和
    # 以后真实 AI 的返回结构保持一致，这样调用方不用改代码


# ===== 5. 定义接口：POST /analyze =====
# @app.post("/analyze") 是装饰器，告诉 FastAPI：
#   "当有人用 POST 方式访问 /analyze 这个网址时，执行下面的函数"
# request 参数的类型是 SentimentRequest —— FastAPI 自动把
# 别人传来的 JSON 解析成这个对象，传错了自动返回 400 报错
@app.post("/analyze")
def analyze(request: SentimentRequest):
    # 取出别人传进来的 text（要分析的句子）
    text = request.text

    # 调用核心分析函数（内部师傅）
    result = analyze_sentiment_mock(text)

    # 返回结果 —— FastAPI 会自动把字典转成 JSON 发给调用方
    # 不用手动 json.dumps，这是 FastAPI 的便利之处
    return result


"""
【总结：这个文件教会你的 4 件事】
1. app = FastAPI()  → 开店（创建接口服务器）
2. class SentimentRequest(BaseModel) → 定收件单格式（请求校验）
3. @app.post("/analyze") → 开窗口（把函数暴露成网址接口）
4. return 字典 → 自动变 JSON 返回给调用方

【下一步（拿到 API Key 后）】
把 analyze_sentiment_mock 内部换成：
    from openai import OpenAI
    client = OpenAI(api_key="你的Key", base_url="https://api.deepseek.com")
    response = client.chat.completions.create(model="deepseek-chat", ...)
    return json.loads(response.choices[0].message.content)
接口层（上面 5 个步骤）完全不用动。
"""
