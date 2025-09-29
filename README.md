# 多用户课表与日程管理工具

一个现代化的、全功能的多用户课表与日程管理 Web 应用。支持个人多课表管理、高级调休功能、完整的团队协作系统，以及灵活的管理员控制功能。专为教育机构和团队协作场景设计。

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

### 个人日程管理
- ✅ **多课表管理**：支持创建多个课表，如"大二上学期"、"大二下学期"等
- ✅ **智能日程导入**：从正方教务系统一键导入课表
- ✅ **灵活的日程编辑**：支持手动创建、编辑和删除日程事件
- ✅ **多视图模式**：周视图和月视图自由切换
- ✅ **课表导出**：支持ICS格式导出，兼容各大日历应用

### 🆕 高级调休功能
- ✅ **节假日设置**：HOLIDAY类型调整，逻辑隐藏指定日期的所有课程
- ✅ **智能换课系统**：SWAP类型调整，将源日期课程完整移动到目标日期
- ✅ **服务器端逻辑**：调休计算在后端处理，确保数据一致性和完整性
- ✅ **调休记录追踪**：完整记录所有调休操作的历史和影响范围
- ✅ **实时生效机制**：调休设置立即在课表视图中反映，无需刷新

### 🆕 团队协作系统
- ✅ **智能邀请机制**：8位随机邀请码（大写字母+数字，避免易混淆字符）
- ✅ **灵活团队管理**：团队创建者自动成为管理员，支持添加/移除成员
- ✅ **分层权限控制**：系统管理员 > 团队创建者 > 普通成员的权限分级
- ✅ **团队课表聚合**：实时查看团队所有成员的课程安排和时间冲突
- ✅ **便捷成员操作**：通过学号添加成员，一键退出/删除团队功能

### 管理员功能
- ✅ **用户管理**：创建、编辑、删除用户账户
- ✅ **课表管理**：查看和管理所有用户的课表
- ✅ **团队监控**：监管所有团队的运行状态
- ✅ **系统设置**：配置头像上传、存储等系统参数

### UI/UX 特性
- ✅ 响应式设计（支持手机、平板、桌面）
- ✅ 简洁的默认风格
- ✅ 现代化交互体验
- ✅ 多色彩用户标识
- ✅ 实时数据更新

## 核心特色

### 🎯 智能调休系统
- **双模式调休架构**：HOLIDAY类型（节假日隐藏）+ SWAP类型（课程对调）
- **服务器端事务处理**：调休操作原子性执行，确保数据完整性
- **事件状态管理**：通过is_active标记实现逻辑删除，保留历史数据
- **覆盖事件机制**：智能创建调整后的新事件，保持原有事件关联
- **操作记录追溯**：ScheduleAdjustment表记录所有调休历史

### 🤝 企业级团队协作
- **安全邀请码生成**：8位大写字母+数字组合，避免易混淆字符(0,O,1,I)
- **多对多关系管理**：用户-团队关联表支持灵活的成员关系
- **权限分层控制**：系统管理员 > 团队创建者 > 普通成员的三级权限
- **课表数据聚合**：跨用户课表查询，支持团队视角的时间安排
- **成员动态管理**：通过学号精确添加，支持实时成员进出

### 📱 现代化用户体验
- **响应式设计**：完美适配桌面、平板和手机
- **模态框交互**：不打断主流程的操作体验
- **实时状态反馈**：操作结果立即反馈给用户
- **直观的视觉设计**：清晰的信息层次和交互指引

### ⚡ 高性能架构
- **前后端分离**：Astro + Vue.js 前端，FastAPI 后端
- **智能状态管理**：Pinia 驱动的响应式状态系统
- **数据库优化**：SQLAlchemy ORM 的高效查询
- **API设计**：RESTful接口设计，支持并发访问

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
- 姓名：黄浩二
- 班级：计工本2303

## 项目结构

```
SDNUChronoSync/
├── backend/                 # 后端代码
│   ├── main.py             # 应用入口
│   ├── models.py           # 数据模型 (User, Schedule, Event, ScheduleAdjustment, Team)
│   ├── schemas.py          # Pydantic 模式 (包含团队和调休相关模式)
│   ├── crud.py             # 数据库操作 (团队CRUD + 调休记录管理)
│   ├── auth.py             # 认证逻辑
│   ├── database.py         # 数据库配置 (含user_teams_table关联表)
│   ├── config.py           # 系统配置
│   ├── utils.py            # 工具函数
│   ├── importer.py         # 教务系统导入
│   ├── services/           # 服务层
│   │   └── uploader_service.py  # 文件上传服务
│   └── routers/            # API 路由
│       ├── auth.py         # 认证路由
│       ├── schedule.py     # 个人日程路由 (废弃)
│       ├── schedules.py    # 🆕 多课表+调休管理路由
│       ├── team.py         # 🆕 完整团队管理路由
│       ├── admin.py        # 管理员路由
│       ├── admin_settings.py # 系统设置路由
│       ├── import_route.py # 教务系统导入路由
│       └── profile.py      # 个人资料路由
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   │   ├── ScheduleAdjuster.vue      # 🆕 调休管理组件（节假日+换课）
│   │   │   ├── ScheduleCalendar.vue      # 日历视图组件（支持调休显示）
│   │   │   ├── ScheduleEditor.vue        # 课表编辑器
│   │   │   ├── ScheduleImporter.vue      # 教务系统导入
│   │   │   ├── MySchedulePage.vue        # 个人课表页面（含调休功能）
│   │   │   ├── MyTeamsPage.vue           # 🆕 我的团队管理页面
│   │   │   ├── TeamViewPage.vue          # 🆕 团队课表聚合视图
│   │   │   ├── CreateTeam.vue            # 🆕 创建团队组件
│   │   │   ├── JoinTeam.vue              # 🆕 加入团队组件
│   │   │   ├── TeamEditorModal.vue       # 🆕 团队编辑模态框
│   │   │   ├── Navigation.vue            # 导航栏（含团队入口）
│   │   │   ├── MobileDrawer.vue          # 移动端菜单
│   │   │   ├── EventModal.vue            # 事件编辑弹窗
│   │   │   └── admin/                    # 管理员组件
│   │   │       └── AdminTeamManagement.vue # 🆕 团队管理组件
│   │   ├── layouts/        # Astro 布局
│   │   │   ├── BaseLayout.astro          # 基础布局
│   │   │   └── DashboardLayout.astro     # 仪表板布局
│   │   ├── pages/          # 页面路由
│   │   │   ├── index.astro               # 首页
│   │   │   ├── login.astro               # 登录页
│   │   │   ├── register.astro            # 注册页
│   │   │   └── dashboard/                # 仪表板页面
│   │   │       ├── my-schedule.astro     # 个人课表（含调休管理）
│   │   │       ├── my-teams.astro        # 🆕 我的团队管理
│   │   │       ├── team-view/            # 🆕 团队视图页面
│   │   │       │   └── [teamId].astro    # 团队详情页
│   │   │       ├── team-view.astro       # 团队视图 (兼容)
│   │   │       ├── profile.astro         # 个人资料
│   │   │       └── admin/                # 管理员页面
│   │   │           └── team-management.astro # 🆕 团队管理页面
│   │   ├── stores/         # Pinia 状态管理
│   │   │   ├── auth.ts                   # 认证状态
│   │   │   ├── schedule.ts               # 课表状态（含调休逻辑）
│   │   │   └── team.ts                   # 🆕 团队状态管理
│   │   ├── types/          # TypeScript 类型定义
│   │   │   └── index.ts                  # 包含Team、ScheduleAdjustment等类型
│   │   └── utils/          # 工具函数
│   │       ├── api.ts                    # API 客户端 (已扩展)
│   │       ├── colors.ts                 # 颜色工具
│   │       └── date.ts                   # 日期工具
│   ├── astro.config.mjs    # Astro 配置
│   ├── tailwind.config.mjs # Tailwind 配置
│   └── package.json        # 依赖管理
├── .gitignore              # Git 忽略文件
├── start_dev.sh            # 开发环境启动脚本
└── README.md               # 项目说明
```

## API 接口

### 认证接口
- `POST /api/auth/token` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/users/me` - 获取当前用户信息

### 课表管理接口
- `GET /api/schedules/` - 获取用户所有课表
- `POST /api/schedules/` - 创建新课表
- `GET /api/schedules/{id}` - 获取指定课表详情
- `PUT /api/schedules/{id}` - 更新课表信息
- `DELETE /api/schedules/{id}` - 删除课表
- `GET /api/schedules/{id}/events` - 获取课表事件（含调休逻辑）
- `POST /api/schedules/{id}/events` - 在课表中创建事件
- `PUT /api/schedules/{id}/events/{event_id}` - 更新课表事件
- `DELETE /api/schedules/{id}/events/{event_id}` - 删除课表事件
- `GET /api/schedules/{id}/export.ics` - 导出课表为ICS文件

### 🆕 调休管理接口
- `GET /api/schedules/{id}/adjustments` - 获取课表的所有调休历史记录
- `POST /api/schedules/{id}/adjustments` - 创建调休调整（HOLIDAY/SWAP类型）
  - **HOLIDAY类型**：`{ "adjustment_type": "HOLIDAY", "holiday_date": "2024-10-01" }`
  - **SWAP类型**：`{ "adjustment_type": "SWAP", "source_date": "2024-10-01", "target_date": "2024-10-02" }`

### 🆕 团队管理接口
- `POST /api/team/` - 创建新团队（自动生成8位邀请码）
- `POST /api/team/me/teams/join` - 通过邀请码加入团队
- `GET /api/team/me/teams` - 获取我参与的所有团队列表
- `GET /api/team/{id}` - 获取团队详细信息（包含成员列表）
- `PUT /api/team/{id}` - 更新团队信息（创建者/管理员）
- `DELETE /api/team/{id}` - 删除团队（创建者/系统管理员）
- `POST /api/team/me/teams/{id}/leave` - 退出团队
- `POST /api/team/{id}/members` - 添加团队成员（通过学号）
- `DELETE /api/team/{id}/members/{user_id}` - 移除团队成员
- `GET /api/team/{id}/schedules` - 获取团队聚合课表视图
- `GET /api/team/all` - 获取所有团队（系统管理员）

### 兼容性接口（团队视图）
- `GET /api/team/users` - 获取所有用户列表
- `GET /api/team/schedule/user/{id}` - 获取指定用户日程
- `GET /api/team/schedule/filtered` - 筛选查询日程

### 个人资料接口
- `GET /api/profile/` - 获取个人资料
- `PUT /api/profile/` - 更新个人资料
- `POST /api/profile/change-password` - 修改密码
- `POST /api/profile/avatar` - 更新头像URL
- `POST /api/profile/upload-avatar` - 上传头像文件
- `GET /api/profile/statistics` - 获取个人统计数据

### 管理员接口
- `GET /api/admin/users` - 获取所有用户（管理员）
- `POST /api/admin/users` - 创建用户
- `PUT /api/admin/users/{id}` - 更新用户
- `DELETE /api/admin/users/{id}` - 删除用户
- `GET /api/admin/settings` - 获取系统设置
- `POST /api/admin/settings` - 更新系统设置
- `POST /api/admin/settings/test-alist` - 测试AList连接

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

## 使用指南

### 🎯 个人课表管理

1. **创建课表**：
   - 访问"我的课表"页面
   - 点击课表下拉菜单中的"新建课表"
   - 设置课表名称、学期开始日期和总周数

2. **导入课程**：
   - 使用"导入"按钮从正方教务系统导入
   - 或手动点击日期添加课程事件

3. **多课表管理**：
   - 支持同时管理多个课表（如不同学期）
   - 通过下拉菜单快速切换活跃课表
   - 每个课表独立管理课程和调休设置

### 🎯 高级调休功能

1. **节假日设置（HOLIDAY类型）**：
   - 在"我的课表"页面点击"日程调整"按钮
   - 选择"设置假期"模式
   - 选择需要放假的日期
   - 点击"确认放假"，系统将逻辑隐藏该日期的所有课程

2. **智能换课（SWAP类型）**：
   - 选择"对调工作日"模式
   - 设置源日期（需要移动的课程日期）
   - 设置目标日期（课程移动到的日期）
   - 系统自动创建覆盖事件，保持原有课程信息

3. **调休记录管理**：
   - 所有调休操作记录在ScheduleAdjustment表中
   - 支持查看调休历史和影响的事件数量
   - 调休效果立即在课表视图中生效

### 🎯 团队协作系统

1. **创建团队**：
   - 访问"我的团队"页面
   - 输入团队名称点击"创建团队"
   - 系统自动生成8位安全邀请码（避免0O1I等易混淆字符）
   - 创建者自动成为团队管理员并加入成员列表

2. **加入团队**：
   - 获取团队8位邀请码
   - 在"加入团队"区域输入邀请码
   - 系统验证邀请码有效性后自动加入团队
   - 支持快速复制邀请码功能

3. **团队管理**：
   - **添加成员**：通过学号精确添加新成员到团队
   - **移除成员**：团队创建者可移除任意成员
   - **权限控制**：系统管理员 > 团队创建者 > 普通成员
   - **团队删除**：仅创建者和系统管理员可删除团队

4. **团队课表聚合**：
   - 查看团队所有成员的课程时间安排
   - 便于协调团队会议和避免时间冲突
   - 支持按成员筛选显示特定用户的课程
   - 实时同步成员的课表变更

### 🎯 管理员功能

1. **用户管理**：
   - 创建、编辑、删除用户账户
   - 重置用户密码和角色权限
   - 查看用户的课表和活动统计

2. **系统设置**：
   - 配置头像上传方式（本地存储/AList）
   - 设置文件上传限制和存储路径
   - 管理系统全局配置参数

3. **团队监控**：
   - 查看所有团队信息
   - 必要时删除团队
   - 监控团队活动和成员状况

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

### v2.0.0 (2025-09-28) - 🆕 高级调休与团队协作系统
**重大功能更新**
- ✅ **多课表管理系统**：支持创建和管理多个课表
- ✅ **高级调休功能**：节假日设置与智能换课系统
- ✅ **完整团队协作**：基于邀请码的团队管理系统
- ✅ **权限分层管理**：团队管理员与普通成员权限控制
- ✅ **团队课表聚合**：查看团队所有成员的课程安排
- ✅ **调休记录管理**：支持撤销和修改调休设置
- ✅ **实时数据同步**：调休和团队变更立即生效
- ✅ **导航系统升级**：新增"我的团队"功能入口
- ✅ **API架构扩展**：新增团队和调休相关接口
- ✅ **数据库模型扩展**：新增Team、TeamMembership、ScheduleAdjustment模型

**技术改进**
- ✅ 服务器端调休逻辑处理，确保数据一致性
- ✅ 完善的错误处理和用户反馈机制
- ✅ 响应式UI适配新功能
- ✅ TypeScript类型系统完善
- ✅ 向后兼容性保证

### v1.2.0 (2025-09-27)
- ✅ 个人资料管理系统
- ✅ 头像上传功能（本地存储/AList支持）
- ✅ 密码修改功能
- ✅ 系统设置管理
- ✅ 教务系统课表导入

### v1.1.0 (2025-09-26)
- ✅ 多课表支持
- ✅ 课表导入功能
- ✅ ICS格式导出
- ✅ 课表状态管理
- ✅ 课程详细信息

### v1.0.0 (2025-09-25)
- ✅ 基础功能完成
- ✅ 用户认证系统
- ✅ 个人日程管理
- ✅ 团队视图功能
- ✅ 管理员功能
- ✅ 响应式 UI 设计
- ✅ 多平台支持
