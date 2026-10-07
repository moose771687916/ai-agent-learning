# Day 20 - Dockerfile（制作镜像的"配方"！）
# 把 agent_app.py 变成可以在任何电脑运行的镜像！

# ① 基础镜像：python官方镜像（国外下载！走代理！）
FROM python:3.12-slim

# ② 设置工作目录（容器里的"当前文件夹"）
WORKDIR /app

# ③ 先复制依赖清单（利用Docker缓存！改代码不用重装依赖！）
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# ④ 复制代码进容器
COPY agent_app.py .

# ⑤ 启动命令：uvicorn跑起来！（0.0.0.0=允许外部访问！）
CMD ["uvicorn", "agent_app:app", "--host", "0.0.0.0", "--port", "8000"]
