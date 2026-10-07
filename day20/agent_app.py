# -*- coding: utf-8 -*-
"""
Day 20 - 要部署的Agent！（一个简单的FastAPI对话服务！）
功能：POST /chat 传一句话 → 智谱大模型回答！
用Docker把它打包部署！（今天的核心！）
"""

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# 从.env读密钥！（容器里也可以用--env-file传！）
load_dotenv()

app = FastAPI()

# 智谱客户端！（免费模型glm-4-flash！）
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)


class ChatRequest(BaseModel):
    message: str  # 用户输入！


@app.get("/")
def home():
    return {"msg": "Day 20 Agent服务运行中！", "接口文档": "/docs"}


@app.post("/chat")
def chat(req: ChatRequest):
    """对话接口：传message → 返回大模型回答！"""
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": req.message}]
    )
    return {"reply": resp.choices[0].message.content}
