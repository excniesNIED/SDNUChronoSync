# 多用户课表与日程管理工具

一个现代化的、响应式的多用户课表与日程管理 Web 应用。支持个人日程管理、团队成员课表互查，以及管理员的用户管理和团队时间协调功能。

## 技术栈

### 前端
- **Astro** - 静态站点生成和路由
- **Vue.ts 3** - 交互式 UI 组件
- **Tailwind CSS** - 响应式样式框架
- **Headless UI** - 无样式 UI 组件
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端

### 后端
- **Python 3.10+** - 编程语言
- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM
- **SQLite** - 数据库
- **JWT** - 用户认证
- **ICS** - 日历导出

## 功能特性

### 用户功能
- ✅ 用户登录/登出
- ✅ 个人课表管理（增删改查）
- ✅ 日历视图（周视图/月视图）
- ✅ 课表导出（ICS 格式）
- ✅ 团队成员课表查看
- ✅ 多维度筛选（日期、成员、班级、年级等）

### 管理员功能
- ✅ 用户管理（增删改查）
- ✅ 全局课表管理
- ✅ 团队时间协调
- ✅ 权限控制

### UI/UX 特性
- ✅ 响应式设计（支持手机、平板、桌面）
- ✅ 简洁的默认风格
- ✅ 现代化交互体验
- ✅ 多色彩用户标识
- ✅ 实时数据更新

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 安装和运行

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd SDNUChronoSync
   ```

2. **后端设置**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   后端服务将在 http://localhost:8000 启动

3. **前端设置**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   前端应用将在 http://localhost:4321 启动

### 默认账户

系统会自动创建以下测试账户：

**管理员账户：**
- 用户名：`admin`
- 密码：`admin123`

**学生账户：**

- 用户名：`202311001145`
- 密码：`password123`
- 姓名：赵恒堂
- 班级：计工本2303

**更多测试账户：**

- `202311001146` / `password123` (李小明 - 计工本2303)
- `202311001147` / `password123` (王小红 - 计工本2304)

## 项目结构

```
SDNUChronoSync/
├── backend/                 # 后端代码
│   ├── main.py             # 应用入口
│   ├── models.py           # 数据模型
│   ├── schemas.py          # Pydantic 模式
│   ├── crud.py             # 数据库操作
│   ├── auth.py             # 认证逻辑
│   ├── database.py         # 数据库配置
│   └── routers/            # API 路由
│       ├── auth.py         # 认证路由
│       ├── schedule.py     # 个人日程路由
│       ├── team.py         # 团队功能路由
│       └── admin.py        # 管理员路由
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── layouts/        # Astro 布局
│   │   ├── pages/          # 页面路由
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── types/          # TypeScript 类型
│   │   └── utils/          # 工具函数
│   ├── astro.config.mjs    # Astro 配置
│   ├── tailwind.config.mjs # Tailwind 配置
│   └── package.json        # 依赖管理
├── .gitignore              # Git 忽略文件
└── README.md               # 项目说明
```

## API 接口

### 认证接口
- `POST /auth/token` - 用户登录
- `GET /auth/users/me` - 获取当前用户信息

### 个人日程接口
- `GET /api/schedule/` - 获取个人日程
- `POST /api/schedule/` - 创建日程
- `PUT /api/schedule/{id}` - 更新日程
- `DELETE /api/schedule/{id}` - 删除日程
- `GET /api/schedule/export/ics` - 导出 ICS 文件

### 团队功能接口
- `GET /api/team/users` - 获取所有用户列表
- `GET /api/team/schedule/user/{id}` - 获取指定用户日程
- `GET /api/team/schedule/filtered` - 筛选查询日程

### 管理员接口
- `GET /api/admin/users` - 获取所有用户（管理员）
- `POST /api/admin/users` - 创建用户
- `PUT /api/admin/users/{id}` - 更新用户
- `DELETE /api/admin/users/{id}` - 删除用户
- `POST /api/admin/schedule/{user_id}` - 为用户创建日程
- `PUT /api/admin/schedule/{id}` - 更新任意日程
- `DELETE /api/admin/schedule/{id}` - 删除任意日程

## 教务系统课表导入

系统支持从山东师范大学正方教务系统导入课表。导入流程如下：

1.  **获取用户课表列表**
    -   `GET /api/import/schedules`
    -   **描述**: 获取当前用户的所有课表列表，用于选择导入目标。
    -   **响应**: 返回课表列表数组。

2.  **获取会话与验证码**
    -   `GET /api/import/zfw/session`
    -   **描述**: 初始化导入流程，返回一个临时的 `session_id` 和 Base64 编码的验证码图片。
    -   **响应**:
        ```json
        {
          "session_id": "string",
          "captcha_image": "string (base64)",
          "source": "string ('real' or 'fallback')"
        }
        ```

3.  **提交登录信息并导入**
    -   `POST /api/import/zfw`
    -   **描述**: 用户输入学号、密码和验证码后，提交至此接口。服务器将尝试登录教务系统，获取、解析课表，并存入指定的课表。
    -   **请求体**:
        ```json
        {
          "session_id": "string",
          "username": "string (学号)",
          "password": "string",
          "captcha": "string (验证码)",
          "action": "string ('create_new' 或 'use_existing')",
          "schedule_id": "integer (action为use_existing时必填)",
          "schedule_name": "string (action为create_new时的课表名称)"
        }
        ```
    -   **响应**:
        ```json
        {
          "success": "boolean",
          "message": "string",
          "imported_count": "integer"
        }
        ```

4.  **刷新验证码 (可选)**
    -   `GET /api/import/zfw/refresh/{session_id}`
    -   **描述**: 如果验证码无法识别，可使用此接口刷新验证码。
    -   **响应**: 返回与获取会话接口相同的结构，但包含新的验证码图片。

## 开发指南

### 后端开发

1. **数据模型修改**：修改 `models.py` 后需要重启服务
2. **API 路由**：在 `routers/` 目录下添加新的路由文件
3. **数据库操作**：在 `crud.py` 中添加新的数据库操作函数

### 前端开发

1. **组件开发**：在 `src/components/` 下创建 Vue 组件
2. **页面路由**：在 `src/pages/` 下创建 Astro 页面
3. **状态管理**：使用 Pinia stores 管理应用状态
4. **样式开发**：使用 Tailwind CSS 类名

## 部署说明

### 开发环境
- 后端：直接运行 `python main.py`
- 前端：运行 `npm run dev`

### 生产环境
- 后端：使用 Gunicorn 或 Uvicorn 部署
- 前端：运行 `npm run build` 生成静态文件，使用 Nginx 等服务器部署

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系我们

如有问题或建议，请通过项目 Issues 提出。

## 更新日志

### v1.0.0 (2025-09-27)
- ✅ 基础功能完成
- ✅ 用户认证系统
- ✅ 个人日程管理
- ✅ 团队视图功能
- ✅ 管理员功能
- ✅ 响应式 UI 设计
- ✅ 多平台支持
