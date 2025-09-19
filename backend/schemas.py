from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    student_id: str = Field(..., description="Student ID, e.g., '202311001145'")
    full_name: str = Field(..., description="Full name, e.g., '赵恒堂'")
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

class UserPublic(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserPublic):
    pass

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

class EventCreate(EventBase):
    owner_id: Optional[int] = None  # For admin use - if not provided, uses current user

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

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    # Include owner information for team views
    owner: Optional[UserPublic] = None

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
    full_name: str = Field(..., description="Full name, e.g., '赵恒堂'")
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

class ImportResponse(BaseModel):
    success: bool
    message: str
    imported_count: Optional[int] = None

# Filter schemas
class ScheduleFilter(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    user_ids: Optional[str] = Field(None, description="Comma-separated user IDs, e.g., '1,5,12'")
    class_name: Optional[str] = None
    grade: Optional[str] = None
    full_name_contains: Optional[str] = None
    event_title_contains: Optional[str] = None
