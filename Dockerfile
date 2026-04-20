# 使用官方轻量级 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，强制 Python 不缓冲 stdout 和 stderr
ENV PYTHONUNBUFFERED=1
# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码到容器中
COPY app.py .

# 暴露 Flask 默认端口
EXPOSE 5000

# 使用 gunicorn 启动服务 (4个工作进程)
# 这里的 app:app 对应 app.py 文件中的 app 变量
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]