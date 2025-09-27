from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Date, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)  # e.g., '202311001145'
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)  # e.g., '黄浩二'
    class_name = Column(String, nullable=False)  # e.g., '计工本2303'
    grade = Column(String, nullable=False)  # e.g., '2023'
    role = Column(String, default="user")  # 'user' or 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with schedules
    schedules = relationship("Schedule", back_populates="owner", cascade="all, delete-orphan")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # 例如："大二上学期"
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 新增的高级属性
    status = Column(String, default="进行")  # "进行", "结束", "隐藏"
    start_date = Column(Date, nullable=False)  # 开学第一天的日期，例如 2025-09-01
    total_weeks = Column(Integer, default=20)  # 课表总周数
    
    # 将1-11节课的默认时间存储为JSON格式
    class_times = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="schedules")
    events = relationship("Event", back_populates="schedule", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)  # 新增
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Fields for detailed course information
    instructor = Column(String, nullable=True)      # 教师
    weeks_display = Column(String, nullable=True)   # 周数 (例: "1-16周")
    day_of_week = Column(Integer, nullable=True)    # 星期几 (1-7)
    period = Column(String, nullable=True)          # 节次 (例: "3-4节")
    weeks_input = Column(String, nullable=True)     # 新增: 用于存储原始输入的周数，如 "1,4-6"
    color = Column(String, nullable=True)           # 课程颜色 (例: "#3B82F6")

    # Relationship with schedule
    schedule = relationship("Schedule", back_populates="events")
