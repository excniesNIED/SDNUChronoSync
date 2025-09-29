from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from models import User, Event, Schedule, Team
from schemas import UserCreate, UserUpdate, EventCreate, EventUpdate, TeamCreate, TeamUpdate
from auth import get_password_hash

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_student_id(db: Session, student_id: str) -> Optional[User]:
    """Get user by student_id."""
    return db.query(User).filter(User.student_id == student_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_data) -> User:
    """Create a new user from UserCreate schema or dict."""
    if isinstance(user_data, dict):
        # Create from dict (for registration)
        db_user = User(**user_data)
    else:
        # Create from UserCreate schema
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            student_id=user_data.student_id,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            class_name=user_data.class_name,
            grade=user_data.grade,
            role=user_data.role
        )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete user and all their events."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

# Event CRUD operations
def get_event(db: Session, event_id: int) -> Optional[Event]:
    """Get event by ID with schedule and owner information."""
    return db.query(Event).options(
        joinedload(Event.schedule).joinedload(Schedule.owner)
    ).filter(Event.id == event_id).first()

def get_user_events(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get all events for a specific user through their schedules."""
    events = db.query(Event).options(
        joinedload(Event.schedule).joinedload(Schedule.owner)
    ).join(Schedule).filter(
        and_(
            Schedule.owner_id == user_id,
            # 与团队视图保持一致的过滤条件
            or_(Event.is_active == True, Event.is_active.is_(None))
        )
    ).offset(skip).limit(limit).all()
    
    # 为每个事件设置 owner 字段
    for event in events:
        if event.schedule and event.schedule.owner:
            event.owner = event.schedule.owner
    
    return events

def create_event(db: Session, event: EventCreate, schedule_id: int) -> Event:
    """Create a new event in a specific schedule."""
    db_event = Event(
        schedule_id=schedule_id,
        title=event.title,
        description=event.description,
        location=event.location,
        start_time=event.start_time,
        end_time=event.end_time,
        instructor=event.instructor,
        weeks_display=event.weeks_display,
        day_of_week=event.day_of_week,
        period=event.period,
        weeks_input=event.weeks_input
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def create_recurring_event(db: Session, event: EventCreate, schedule_id: int) -> List[Event]:
    """Create recurring events based on weeks_input range."""
    from utils import parse_weeks
    from datetime import timedelta, datetime
    
    # 获取课表信息
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise ValueError("Schedule not found")
    
    # 解析周数
    weeks = parse_weeks(event.weeks_input or event.weeks_display or "")
    if not weeks:
        # 如果没有周数信息，创建单个事件
        return [create_event(db, event, schedule_id)]
    
    created_events = []
    
    for week_number in weeks:
        # 计算这一周对应的具体日期
        if event.day_of_week and schedule.start_date:
            # 计算从课表开始到目标周的天数
            # 周一=1对应offset=0，周二=2对应offset=1，...，周日=7对应offset=6
            day_offset = event.day_of_week - 1
            total_days = (week_number - 1) * 7 + day_offset
            
            target_date = schedule.start_date + timedelta(days=total_days)
            
            # 提取原始事件的时间部分
            original_start = event.start_time
            original_end = event.end_time
            
            # 合并日期和时间
            if isinstance(original_start, datetime) and isinstance(original_end, datetime):
                new_start_time = datetime.combine(
                    target_date, 
                    original_start.time()
                )
                new_end_time = datetime.combine(
                    target_date, 
                    original_end.time()
                )
            else:
                # 如果时间不是datetime对象，使用原始时间
                new_start_time = original_start
                new_end_time = original_end
        else:
            # 如果没有day_of_week或start_date信息，使用原始时间
            new_start_time = event.start_time
            new_end_time = event.end_time
        
        # 创建这一周的事件
        week_event = Event(
            schedule_id=schedule_id,
            title=event.title,
            description=event.description,
            location=event.location,
            start_time=new_start_time,
            end_time=new_end_time,
            instructor=event.instructor,
            weeks_display=f"第{week_number}周",
            weeks_input=str(week_number),
            day_of_week=event.day_of_week,
            period=event.period
        )
        
        db.add(week_event)
        created_events.append(week_event)
    
    db.commit()
    
    # 刷新所有创建的事件
    for event_obj in created_events:
        db.refresh(event_obj)
    
    return created_events

def update_event(db: Session, event_id: int, event_update: EventUpdate) -> Optional[Event]:
    """Update event."""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db_event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int) -> bool:
    """Delete event."""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return False
    
    db.delete(db_event)
    db.commit()
    return True

def get_filtered_events(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    user_ids: Optional[List[int]] = None,
    team_ids: Optional[List[int]] = None,
    class_names: Optional[List[str]] = None,
    grades: Optional[List[str]] = None,
    full_name_contains: Optional[str] = None,
    event_title_contains: Optional[str] = None
) -> List[Event]:
    """Get filtered events with complex query conditions."""
    
    # Use proper relationships: Event -> Schedule -> User
    query = db.query(Event).options(
        joinedload(Event.schedule).joinedload(Schedule.owner)
    )
    
    # Filter by date range
    query = query.filter(
        and_(
            Event.start_time >= start_date,
            Event.end_time <= end_date
        )
    )
    
    # Join with Schedule and User tables for user-based filters
    query = query.join(Schedule).join(User)
    
    # Filter by specific user IDs
    if user_ids:
        query = query.filter(User.id.in_(user_ids))
    
    # Filter by team IDs - get users from selected teams
    if team_ids:
        # Get all user IDs from the selected teams
        team_users = db.query(User).join(User.teams).filter(Team.id.in_(team_ids)).all()
        team_user_ids = [user.id for user in team_users]
        if team_user_ids:
            if user_ids:
                # If both user_ids and team_ids are provided, use intersection
                combined_ids = list(set(user_ids) & set(team_user_ids))
                query = query.filter(User.id.in_(combined_ids))
            else:
                # If only team_ids provided, use team member IDs
                query = query.filter(User.id.in_(team_user_ids))
        else:
            # No users found in selected teams, return empty result
            return []
    
    # Filter by class names
    if class_names:
        class_conditions = [User.class_name.ilike(f"%{cn}%") for cn in class_names]
        query = query.filter(or_(*class_conditions))
    
    # Filter by grades
    if grades:
        grade_conditions = [User.grade.ilike(f"%{g}%") for g in grades]
        query = query.filter(or_(*grade_conditions))
    
    # Filter by full name
    if full_name_contains:
        query = query.filter(User.full_name.ilike(f"%{full_name_contains}%"))
    
    # Filter by event title
    if event_title_contains:
        query = query.filter(Event.title.ilike(f"%{event_title_contains}%"))
    
    # 获取事件并手动设置owner字段
    events = query.all()
    
    # 为每个事件设置 owner 字段
    for event in events:
        if event.schedule and event.schedule.owner:
            event.owner = event.schedule.owner
    
    return events


# Team CRUD operations
def get_team(db: Session, team_id: int) -> Optional[Team]:
    """Get team by ID with creator and members."""
    return db.query(Team).options(
        joinedload(Team.creator),
        joinedload(Team.members)
    ).filter(Team.id == team_id).first()

def get_team_by_code(db: Session, team_code: str) -> Optional[Team]:
    """Get team by team code."""
    return db.query(Team).options(
        joinedload(Team.creator),
        joinedload(Team.members)
    ).filter(Team.team_code == team_code).first()

def get_user_teams(db: Session, user_id: int) -> List[Team]:
    """Get all teams that a user belongs to."""
    user = db.query(User).options(joinedload(User.teams)).filter(User.id == user_id).first()
    return user.teams if user else []

def get_all_teams(db: Session, skip: int = 0, limit: int = 100) -> List[Team]:
    """Get all teams with creator and members information."""
    return db.query(Team).options(
        joinedload(Team.creator),
        joinedload(Team.members)
    ).offset(skip).limit(limit).all()

def create_team(db: Session, team: TeamCreate, creator_id: int) -> Team:
    """Create a new team."""
    team_code = Team.generate_team_code(db)
    db_team = Team(
        name=team.name,
        team_code=team_code,
        creator_id=creator_id
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    # Automatically add creator as a member
    creator = db.query(User).filter(User.id == creator_id).first()
    if creator:
        db_team.members.append(creator)
        db.commit()
        db.refresh(db_team)
    
    return db_team

def update_team(db: Session, team_id: int, team_update: TeamUpdate) -> Optional[Team]:
    """Update team information."""
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        return None
    
    update_data = team_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_team, field, value)
    
    db_team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_team)
    return db_team

def add_team_member(db: Session, team_id: int, user_id: int) -> bool:
    """Add a user to a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not team or not user:
        return False
    
    if user not in team.members:
        team.members.append(user)
        db.commit()
    
    return True

def remove_team_member(db: Session, team_id: int, user_id: int) -> bool:
    """Remove a user from a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not team or not user:
        return False
    
    if user in team.members:
        team.members.remove(user)
        db.commit()
    
    return True

def join_team_by_code(db: Session, team_code: str, user_id: int) -> Optional[Team]:
    """Join a team using team code."""
    team = get_team_by_code(db, team_code)
    if not team:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    if user not in team.members:
        team.members.append(user)
        db.commit()
        db.refresh(team)
    
    return team

def get_team_schedules_events(db: Session, team_id: int) -> List[Event]:
    """Get all events from active schedules of team members."""
    team = db.query(Team).options(joinedload(Team.members)).filter(Team.id == team_id).first()
    if not team:
        return []
    
    # Get all member IDs
    member_ids = [member.id for member in team.members]
    
    if not member_ids:
        return []
    
    # Get all events from team members' schedules (removed strict filters for debugging)
    events = db.query(Event).options(
        joinedload(Event.schedule).joinedload(Schedule.owner)
    ).join(Schedule).filter(
        and_(
            Schedule.owner_id.in_(member_ids),
            # Removed strict status and is_active filters to show all events
            or_(Event.is_active == True, Event.is_active.is_(None))  # Include events where is_active is True or NULL
        )
    ).all()
    
    # Set owner field for each event
    for event in events:
        if event.schedule and event.schedule.owner:
            event.owner = event.schedule.owner
    
    return events

def delete_team(db: Session, team_id: int) -> bool:
    """Delete a team."""
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        return False
    
    db.delete(db_team)
    db.commit()
    return True

def is_team_creator(db: Session, team_id: int, user_id: int) -> bool:
    """Check if a user is the creator of a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    return team and team.creator_id == user_id

def is_team_member(db: Session, team_id: int, user_id: int) -> bool:
    """Check if a user is a member of a team."""
    user = db.query(User).options(joinedload(User.teams)).filter(User.id == user_id).first()
    if not user:
        return False
    
    return any(team.id == team_id for team in user.teams)
