from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)  # e.g., '202311001145'
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)  # e.g., '赵恒堂'
    class_name = Column(String, nullable=False)  # e.g., '计工本2303'
    grade = Column(String, nullable=False)  # e.g., '2023'
    role = Column(String, default="user")  # 'user' or 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with events
    events = relationship("Event", back_populates="owner", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New fields for detailed course information
    instructor = Column(String, nullable=True)      # 教师
    weeks_display = Column(String, nullable=True)   # 周数 (例: "1-16周")
    day_of_week = Column(Integer, nullable=True)    # 星期几 (1-7)
    period = Column(String, nullable=True)          # 节次 (例: "3-4节")

    # Relationship with user
    owner = relationship("User", back_populates="events")
