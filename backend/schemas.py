from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

# User schemas
class UserBase(BaseModel):
    student_id: str = Field(..., description="Student ID, e.g., '202311001145'")
    full_name: str = Field(..., description="Full name, e.g., '黄浩二'")
    class_name: str = Field(..., description="Class name, e.g., '计工本2303'")
    grade: str = Field(..., description="Grade, e.g., '2023'")

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    student_id: Optional[str] = None
    full_name: Optional[str] = None
    class_name: Optional[str] = None
    grade: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None

class UpdateUserRequest(BaseModel):
    """用于个人中心更新个人信息的请求模型"""
    full_name: Optional[str] = None
    class_name: Optional[str] = None
    grade: Optional[str] = None

class UserPublic(UserBase):
    id: int
    role: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(UserPublic):
    pass

# Schedule schemas
class ScheduleBase(BaseModel):
    name: str = Field(..., description="Schedule name, e.g., '大二上学期'")
    status: str = Field(default="进行", description="Status: '进行', '结束', '隐藏'")
    start_date: date = Field(..., description="Start date of the semester")
    total_weeks: int = Field(default=20, description="Total weeks in the schedule")
    class_times: Dict[str, Dict[str, str]] = Field(..., description="Class time slots")

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    total_weeks: Optional[int] = None
    class_times: Optional[Dict[str, Dict[str, str]]] = None

class ScheduleResponse(ScheduleBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Event schemas
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    instructor: Optional[str] = None      # 教师
    weeks_display: Optional[str] = None   # 周数 (例: "1-16周")
    day_of_week: Optional[int] = None     # 星期几 (1-7)
    period: Optional[str] = None          # 节次 (例: "3-4节")
    weeks_input: Optional[str] = None     # 新增: 原始输入的周数，如 "1,4-6"
    color: Optional[str] = None           # 课程颜色

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    instructor: Optional[str] = None
    weeks_display: Optional[str] = None
    day_of_week: Optional[int] = None
    period: Optional[str] = None
    weeks_input: Optional[str] = None

class EventResponse(EventBase):
    id: int
    schedule_id: int
    created_at: datetime
    updated_at: datetime
    
    # Include schedule and owner information for team views
    schedule: Optional['ScheduleResponse'] = None
    owner: Optional[UserPublic] = None  # 直接包含 owner 字段

    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    student_id: Optional[str] = None

class LoginRequest(BaseModel):
    student_id: str
    password: str

class RegisterRequest(BaseModel):
    student_id: str = Field(..., description="Student ID, e.g., '202311001145'")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    full_name: str = Field(..., description="Full name, e.g., '黄浩二'")
    class_name: str = Field(..., description="Class name, e.g., '计工本2303'")
    grade: str = Field(..., description="Grade, e.g., '2023'")

# Import schemas
class ImportSessionResponse(BaseModel):
    session_id: str
    csrftoken: str
    captcha_image: str  # base64 encoded image

class ImportRequest(BaseModel):
    session_id: str
    username: str
    password: str
    captcha: str
    schedule_id: Optional[int] = None  # 指定要导入到的课表ID，如果为None则创建新课表
    action: str = "create_new"  # "use_existing" 或 "create_new"
    schedule_name: Optional[str] = None  # 创建新课表时的名称
    start_date: Optional[date] = None  # 开学日期，仅在创建新课表时生效

class ImportResponse(BaseModel):
    success: bool
    message: str
    imported_count: Optional[int] = None
    user_info: Optional[Dict[str, Any]] = None  # 用户信息字典

# Filter schemas
class ScheduleFilter(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    user_ids: Optional[str] = Field(None, description="Comma-separated user IDs, e.g., '1,5,12'")
    class_name: Optional[str] = None
    grade: Optional[str] = None
    full_name_contains: Optional[str] = None
    event_title_contains: Optional[str] = None
