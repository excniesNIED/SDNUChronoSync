from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Date, JSON, Table
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import secrets

# Association table for many-to-many relationship between users and teams
user_teams_table = Table('user_teams', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)  # e.g., '202311001145'
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)  # e.g., '黄浩二'
    class_name = Column(String, nullable=False)  # e.g., '计工本2303'
    grade = Column(String, nullable=False)  # e.g., '2023'
    role = Column(String, default="user")  # 'user' or 'admin'
    avatar_url = Column(String, nullable=True)  # 头像URL
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with schedules
    schedules = relationship("Schedule", back_populates="owner", cascade="all, delete-orphan")
    
    # Relationship with teams (many-to-many)
    teams = relationship("Team", secondary=user_teams_table, back_populates="members")

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
    adjustments = relationship("ScheduleAdjustment", back_populates="schedule", cascade="all, delete-orphan")

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
    
    # Fields for schedule adjustment
    is_override = Column(Boolean, default=False)    # 是否为调休覆盖事件
    is_active = Column(Boolean, default=True)       # 是否激活（用于逻辑删除）
    adjustment_id = Column(Integer, ForeignKey('schedule_adjustments.id'), nullable=True)  # 关联调整操作

    # Relationship with schedule
    schedule = relationship("Schedule", back_populates="events")
    # Relationship with adjustment
    adjustment = relationship("ScheduleAdjustment", back_populates="override_events")


class ScheduleAdjustment(Base):
    __tablename__ = 'schedule_adjustments'
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=False)
    
    # 操作类型: 'HOLIDAY' (放假), 'SWAP' (交换)
    adjustment_type = Column(String, nullable=False)
    
    # 原始日期 (被操作的日期)
    original_date = Column(Date, nullable=False)
    
    # 目标日期 (课程被移动到的日期, 'HOLIDAY'类型下此字段为空)
    target_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="adjustments")
    override_events = relationship("Event", back_populates="adjustment")


class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    team_code = Column(String, unique=True, index=True, nullable=False)  # 随机生成的唯一加入代码
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 明确指定团队的创建者
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id])
    members = relationship("User", secondary=user_teams_table, back_populates="teams")
    
    @classmethod
    def generate_team_code(cls, db_session=None):
        """Generate a unique 8-character team code"""
        while True:
            # Generate a random 8-character code with letters and numbers
            team_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            
            # Check if it already exists (if db_session is provided)
            if db_session is None or not db_session.query(cls).filter(cls.team_code == team_code).first():
                return team_code
