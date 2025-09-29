# SDNUChronoSync 部署指南

多用户课表与日程管理工具的完整部署指南，支持三种部署方式。

## 📋 目录

- [系统要求](#系统要求)
- [部署方式](#部署方式)
  - [1. Docker Compose 部署 (推荐)](#1-docker-compose-部署-推荐)
  - [2. Docker 单容器部署](#2-docker-单容器部署)
  - [3. 源码部署 (npm + python)](#3-源码部署-npm--python)
- [容器持久化配置](#容器持久化配置)
- [环境配置](#环境配置)
- [故障排除](#故障排除)

## 📦 系统要求

### Docker 部署
- Docker 20.0+ 
- Docker Compose 2.0+
- 可用内存: 1GB+
- 可用磁盘: 2GB+

### 源码部署
- Python 3.11+
- Node.js 18+
- npm 或 yarn
- 可用内存: 512MB+
- 可用磁盘: 1GB+

## 🚀 部署方式

### 1. Docker Compose 部署 (推荐)

最简单的一键部署方式，适合生产环境使用。

#### 快速启动

```bash
# 1. 克隆项目
git clone <repository-url>
cd SDNUChronoSync

# 2. 创建数据目录
mkdir -p data/{database,uploads,config,logs}

# 3. 复制配置文件
cp backend/config.toml data/config/

# 4. 启动服务
docker-compose up -d

# 5. 查看服务状态
docker-compose ps
```

#### 服务访问

- **应用地址**: http://localhost:1145
- **API文档**: http://localhost:1145/docs
- **健康检查**: http://localhost:1145/health

#### 管理命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 进入容器
docker-compose exec sdnu-chronosync bash

# 备份数据
docker-compose exec sdnu-chronosync cp /app/schedule_app.db /app/backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. Docker 单容器部署

适合简单部署场景，手动管理数据持久化。

#### 构建镜像

```bash
# 1. 构建镜像
docker build -t sdnu-chronosync:latest .

# 2. 创建数据卷
docker volume create sdnu-data
docker volume create sdnu-uploads
docker volume create sdnu-config
docker volume create sdnu-logs

# 3. 运行容器
docker run -d \
  --name sdnu-chronosync \
  -p 1145:1145 \
  -v sdnu-data:/app/schedule_app.db \
  -v sdnu-uploads:/app/uploads \
  -v sdnu-config:/app/config.toml \
  -v sdnu-logs:/app/logs \
  --restart unless-stopped \
  sdnu-chronosync:latest
```

#### 管理命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs sdnu-chronosync -f

# 停止容器
docker stop sdnu-chronosync

# 启动容器
docker start sdnu-chronosync

# 删除容器
docker rm sdnu-chronosync

# 备份数据
docker cp sdnu-chronosync:/app/schedule_app.db ./backup_$(date +%Y%m%d_%H%M%S).db
```

### 3. 源码部署 (npm + python)

适合开发环境或需要自定义的场景。

#### 环境准备

```bash
# 1. 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 2. 安装 Node.js 依赖
cd ../frontend
npm install

# 3. 构建前端
npm run build
```

#### 启动服务

##### 方式一：使用启动脚本 (推荐)

```bash
# 项目根目录下
chmod +x start_dev.sh
./start_dev.sh
```

##### 方式二：手动启动

```bash
# 终端1: 启动后端 (端口8000)
cd backend
python main.py

# 终端2: 启动前端 (端口4321)
cd frontend
npm run dev

# 终端3: 使用 nginx 反向代理到1145端口 (可选)
# 配置 nginx.conf 将请求转发到对应服务
```

#### 生产环境部署

```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 配置生产环境服务器 (nginx + gunicorn)
# nginx 配置示例：
server {
    listen 1145;
    server_name your-domain.com;
    
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ @backend;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location @backend {
        proxy_pass http://127.0.0.1:8000;
    }
}

# 3. 使用 gunicorn 启动后端
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 💾 容器持久化配置

### 数据持久化策略

容器化部署需要将重要数据持久化到宿主机，确保容器重启后数据不丢失。

#### 1. Docker Compose 持久化 (自动配置)

使用 `docker-compose.yml` 会自动创建以下挂载：

```yaml
volumes:
  # 数据库文件
  - ./data/database:/app/schedule_app.db
  # 用户上传文件
  - ./data/uploads:/app/uploads  
  # 配置文件
  - ./data/config:/app/config.toml
  # 应用日志
  - ./data/logs:/app/logs
```

#### 2. Docker 单容器持久化 (手动配置)

```bash
# 创建宿主机目录
mkdir -p ~/sdnu-data/{database,uploads,config,logs}

# 复制初始配置
cp backend/config.toml ~/sdnu-data/config/

# 运行容器并挂载目录
docker run -d \
  --name sdnu-chronosync \
  -p 1145:1145 \
  -v ~/sdnu-data/database:/app \
  -v ~/sdnu-data/uploads:/app/uploads \
  -v ~/sdnu-data/config/config.toml:/app/config.toml \
  -v ~/sdnu-data/logs:/app/logs \
  sdnu-chronosync:latest
```

#### 3. 数据备份策略

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份数据库
cp ./data/database/schedule_app.db "$BACKUP_DIR/"

# 备份上传文件
cp -r ./data/uploads "$BACKUP_DIR/"

# 备份配置
cp ./data/config/config.toml "$BACKUP_DIR/"

echo "备份完成: $BACKUP_DIR"
EOF

chmod +x backup.sh

# 设置定时备份 (可选)
# crontab -e
# 0 2 * * * /path/to/backup.sh
```

### 重要目录说明

| 目录/文件 | 用途 | 是否必须持久化 |
|-----------|------|---------------|
| `/app/schedule_app.db` | SQLite数据库文件 | ✅ 必须 |
| `/app/uploads/avatars/` | 用户头像文件 | ✅ 推荐 |
| `/app/config.toml` | 应用配置文件 | ✅ 推荐 |
| `/app/logs/` | 应用日志文件 | 📝 可选 |

## ⚙️ 环境配置

### 配置文件说明

主配置文件：`config.toml`

```toml
[storage]
provider = "local"  # 或 "alist"

[storage.local]
upload_path = "uploads/avatars"
base_url = "/static/avatars"

[storage.alist]
version = 3
url = "https://your-alist-instance.com"
upload_path = "your-upload-path"
token = "your-token"
username = "your-username"
password = "your-password"
```

### 环境变量 (Docker)

```bash
# .env 文件示例
NODE_ENV=production
PYTHONUNBUFFERED=1

# 可选：数据库配置
# DATABASE_URL=sqlite:///./schedule_app.db

# 可选：外部存储配置
# STORAGE_PROVIDER=alist
# ALIST_URL=https://your-alist.com
# ALIST_TOKEN=your-token
```

### 默认账户

系统启动后会自动创建默认账户：

- **管理员账户**
  - 用户名: `admin`
  - 密码: `admin123`
  - 权限: 管理员

- **测试学生账户**
  - 用户名: `202311001145`
  - 密码: `password123`
  - 权限: 普通用户

⚠️ **安全提醒**: 生产环境请及时修改默认密码！

## 🔧 故障排除

### 常见问题

#### 1. 容器无法启动

```bash
# 检查端口占用
netstat -tulpn | grep 1145

# 检查容器日志
docker-compose logs sdnu-chronosync

# 检查资源使用
docker stats
```

#### 2. 数据库连接失败

```bash
# 检查数据库文件权限
ls -la data/database/

# 重新初始化数据库
docker-compose exec sdnu-chronosync python -c "from main import init_db; init_db()"
```

#### 3. 文件上传失败

```bash
# 检查上传目录权限
ls -la data/uploads/

# 修复权限
chmod -R 755 data/uploads/
```

#### 4. 前端资源加载失败

```bash
# 重新构建镜像
docker-compose up -d --build

# 检查 nginx 配置
docker-compose exec sdnu-chronosync nginx -t
```

### 日志查看

```bash
# 应用日志
docker-compose logs -f sdnu-chronosync

# 后端API日志
docker-compose exec sdnu-chronosync tail -f logs/fastapi.log

# Nginx日志
docker-compose exec sdnu-chronosync tail -f logs/nginx.log

# 系统监控
docker-compose exec sdnu-chronosync top
```

### 性能优化

```bash
# 增加工作进程数 (修改 supervisord.conf)
command=uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 数据库优化
# 定期清理日志和临时文件
# 考虑使用外部数据库 (PostgreSQL/MySQL)
```

## 📞 技术支持

如果遇到问题，请检查：

1. 系统资源是否充足
2. 端口是否被占用
3. 数据目录权限是否正确
4. 防火墙是否阻止访问

更多帮助请查看项目文档或提交Issue。

---

🎉 **部署完成后，访问 http://localhost:1145 开始使用！**
