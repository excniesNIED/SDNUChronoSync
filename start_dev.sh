#!/bin/bash

# 多用户课表与日程管理工具 - 开发环境启动脚本

echo "🚀 启动多用户课表与日程管理工具开发环境"
echo "=================================="

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ Python 未找到，请先安装 Python 3.10+"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未找到，请先安装 Node.js 18+"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端服务器
echo "🔧 启动后端服务器..."
cd backend
python main.py &
BACKEND_PID=$!
echo "✅ 后端服务器已启动 (PID: $BACKEND_PID) - http://localhost:8000"
echo ""

# 等待后端启动
sleep 3

# 启动前端开发服务器
echo "🎨 启动前端开发服务器..."
cd ../frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ 前端开发服务器已启动 (PID: $FRONTEND_PID) - http://localhost:4321"
echo ""

echo "🎉 开发环境启动完成！"
echo "=================================="
echo "📱 前端应用: http://localhost:4321"
echo "🔧 后端 API: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""
echo "默认测试账户："
echo "👤 管理员: admin / admin123"
echo "🎓 学生: 202311001145 / password123"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "=================================="

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
