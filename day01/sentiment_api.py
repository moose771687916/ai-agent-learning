# -*- coding: utf-8 -*-
"""
情感分析接口（真实版）—— 调用智谱 AI 大模型
=================================================

【这个文件和模拟版的关系】
模拟版（sentiment_api_mock.py）用关键词规则假装分析；
这个版本把"内部师傅"换成了真实的大模型（智谱 GLM）。
接口部分（/analyze、请求格式、返回结构）和模拟版一模一样——
这就是我们说的：接口层不变，只换里面的师傅。

【为什么用智谱】
- 新用户送 2000 万 token，免费额度足够学习用很久
- 接口完全兼容 OpenAI 格式，代码和 DeepSeek 通用
- 用免费模型 glm-4-flash（永久免费）

【怎么运行】
    python -m uvicorn sentiment_api:app --reload
然后浏览器打开 http://127.0.0.1:8000/docs 测试

【安全提醒】
API Key 相当于你的"账户密码"。这个文件不要上传到
GitHub 等公开平台。以后可以学用 .env 文件存 Key（更安全）。
"""

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv  # 读取 .env 文件的小工具
import json
import os  # os.environ 是 Python 访问环境变量的入口

# ===== 1. 创建应用 =====
app = FastAPI(title="情感分析接口（真实 AI 版）")

# ===== 2. 初始化大模型客户端 =====
# 【环境变量方式】Key 存在同目录的 .env 文件里（保险箱），
# load_dotenv() 把 .env 里的内容读进来，os.getenv() 再取出来。
# 好处：代码里没有真实 Key，就算代码泄露，Key 还在保险箱里。
load_dotenv()  # 读取 .env 文件
api_key = os.getenv("ZHIPU_API_KEY")  # 从环境变量取 Key（.env 里配的）

# 智谱的接口地址（兼容 OpenAI 协议，所以用 openai 库）
# 模型名：glm-4-flash 是智谱的免费模型
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4"  # 智谱的地址
)
MODEL_NAME = "glm-4-flash"

# ===== 3. 定义请求格式 =====
class SentimentRequest(BaseModel):
    text: str  # 要分析的句子

# ===== 4. 情感分析核心函数（真实 AI 版） =====
# 用的就是 Day1 学的结构化输出套路：
#   system prompt 规定格式 + 给示例 + temperature 调低
def analyze_sentiment(text: str):
    system_prompt = """
    你是一个情感分析助手。分析用户输入的句子，返回JSON格式结果。

    必须严格按以下JSON格式输出，不要输出任何其他文字：
    {
      "sentiment": "positive/negative/neutral",
      "confidence": 0到1之间的小数,
      "keywords": ["关键词1", "关键词2"]
    }

    示例：
    用户：今天天气真好，心情特别棒！
    返回：{"sentiment": "positive", "confidence": 0.98, "keywords": ["天气好", "心情棒"]}

    用户：这个产品太烂了，再也不买了。
    返回：{"sentiment": "negative", "confidence": 0.95, "keywords": ["产品烂", "不买"]}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    # 调用大模型（和 DeepSeek 的写法完全一样，因为接口兼容）
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.1  # 结构化任务调低，保证输出稳定
    )

    result_text = response.choices[0].message.content
    print(f"AI原始返回：{result_text}")

    # 把 AI 返回的 JSON 字符串转成字典
    try:
        return json.loads(result_text)
    except:
        # AI 偶尔会不守规矩，必须做异常处理防崩溃（Day1 学的）
        return {"error": "AI返回格式异常", "raw": result_text}

# ===== 5. 定义接口：POST /analyze =====
@app.post("/analyze")
def analyze(request: SentimentRequest):
    result = analyze_sentiment(request.text)
    return result
