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

class EventCreate(EventBase):
    owner_id: Optional[int] = None  # For admin use - if not provided, uses current user

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

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

# Filter schemas
class ScheduleFilter(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    user_ids: Optional[str] = Field(None, description="Comma-separated user IDs, e.g., '1,5,12'")
    class_name: Optional[str] = None
    grade: Optional[str] = None
    full_name_contains: Optional[str] = None
    event_title_contains: Optional[str] = None
