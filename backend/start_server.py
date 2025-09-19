#!/usr/bin/env python3
"""
多用户课表与日程管理工具 - 服务器启动脚本
"""

import uvicorn
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动FastAPI服务器"""
    print("🚀 启动多用户课表与日程管理工具后端服务器")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()