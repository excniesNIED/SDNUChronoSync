from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from models import User, Event
from schemas import UserCreate, UserUpdate, EventCreate, EventUpdate
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

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        student_id=user.student_id,
        hashed_password=hashed_password,
        full_name=user.full_name,
        class_name=user.class_name,
        grade=user.grade,
        role=user.role
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
    """Get event by ID with owner information."""
    return db.query(Event).options(joinedload(Event.owner)).filter(Event.id == event_id).first()

def get_user_events(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get all events for a specific user."""
    return db.query(Event).options(joinedload(Event.owner)).filter(Event.owner_id == user_id).offset(skip).limit(limit).all()

def create_event(db: Session, event: EventCreate, owner_id: int) -> Event:
    """Create a new event."""
    db_event = Event(
        title=event.title,
        description=event.description,
        location=event.location,
        start_time=event.start_time,
        end_time=event.end_time,
        owner_id=owner_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

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
    class_name: Optional[str] = None,
    grade: Optional[str] = None,
    full_name_contains: Optional[str] = None,
    event_title_contains: Optional[str] = None
) -> List[Event]:
    """Get filtered events with complex query conditions."""
    
    query = db.query(Event).options(joinedload(Event.owner))
    
    # Filter by date range
    query = query.filter(
        and_(
            Event.start_time >= start_date,
            Event.end_time <= end_date
        )
    )
    
    # Join with User table for user-based filters
    query = query.join(User)
    
    # Filter by specific user IDs
    if user_ids:
        query = query.filter(User.id.in_(user_ids))
    
    # Filter by class name
    if class_name:
        query = query.filter(User.class_name.ilike(f"%{class_name}%"))
    
    # Filter by grade
    if grade:
        query = query.filter(User.grade.ilike(f"%{grade}%"))
    
    # Filter by full name
    if full_name_contains:
        query = query.filter(User.full_name.ilike(f"%{full_name_contains}%"))
    
    # Filter by event title
    if event_title_contains:
        query = query.filter(Event.title.ilike(f"%{event_title_contains}%"))
    
    return query.all()
