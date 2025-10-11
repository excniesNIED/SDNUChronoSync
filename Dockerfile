# 多阶段构建 Dockerfile - 前后端一体
FROM node:20-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 复制前端 package 文件
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm ci --only=production

# 复制前端源码
COPY frontend/ .

# 构建前端应用
RUN npm run build

# Python 运行时基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV NODE_ENV=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 创建应用目录
WORKDIR /app

# 复制后端requirements文件
COPY backend/requirements.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./

# 从前端构建阶段复制构建结果
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建必要的目录
RUN mkdir -p uploads/avatars logs

# 复制配置文件
COPY backend/config.toml ./

# 配置 Nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 配置 Supervisor
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 暴露端口
EXPOSE 1145

# 启动 Supervisor (管理 FastAPI 和 Nginx)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
