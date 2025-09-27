from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse, EventCreate, EventUpdate, EventResponse
from auth import get_current_admin_user
from models import User, Schedule
import crud

router = APIRouter(prefix="/api/admin", tags=["admin management"])

# User management endpoints
@router.get("/users", response_model=List[UserResponse])
async def get_all_users_admin(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with complete information (admin only)."""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/users", response_model=UserResponse)
async def create_user_admin(
    user: UserCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)."""
    # Check if user with this student_id already exists
    existing_user = crud.get_user_by_student_id(db, user.student_id)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this student ID already exists"
        )
    
    db_user = crud.create_user(db, user)
    return db_user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)."""
    # Check if user exists
    existing_user = crud.get_user(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If updating student_id, check for conflicts
    if user_update.student_id:
        conflicting_user = crud.get_user_by_student_id(db, user_update.student_id)
        if conflicting_user and conflicting_user.id != user_id:
            raise HTTPException(
                status_code=400,
                detail="Another user with this student ID already exists"
            )
    
    updated_user = crud.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user_admin(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user and all their events (admin only)."""
    # Prevent admin from deleting themselves
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own admin account"
        )
    
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User and all associated events deleted successfully"}

# Schedule management endpoints
@router.post("/schedule/{user_id}", response_model=EventResponse)
async def create_event_for_user(
    user_id: int,
    event: EventCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create an event for a specific user (admin only)."""
    # Check if target user exists
    target_user = crud.get_user(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create user's default schedule
    user_schedule = db.query(Schedule).filter(Schedule.owner_id == user_id).first()
    
    if not user_schedule:
        # Create default schedule for the user
        from datetime import date
        default_class_times = {
            "1": {"start": "08:00", "end": "08:45"},
            "2": {"start": "08:50", "end": "09:35"},
            "3": {"start": "09:50", "end": "10:35"},
            "4": {"start": "10:40", "end": "11:25"},
            "5": {"start": "11:30", "end": "12:15"},
            "6": {"start": "14:00", "end": "14:45"},
            "7": {"start": "14:50", "end": "15:35"},
            "8": {"start": "15:50", "end": "16:35"},
            "9": {"start": "16:40", "end": "17:25"},
            "10": {"start": "19:00", "end": "19:45"},
            "11": {"start": "19:50", "end": "20:35"}
        }
        
        user_schedule = Schedule(
            name=f"{target_user.full_name}的课表",
            owner_id=user_id,
            status="进行",
            start_date=date(2024, 9, 1),
            total_weeks=20,
            class_times=default_class_times
        )
        db.add(user_schedule)
        db.commit()
        db.refresh(user_schedule)
    
    db_event = crud.create_event(db, event, user_schedule.id)
    # Reload with owner information
    return crud.get_event(db, db_event.id)

@router.put("/schedule/{event_id}", response_model=EventResponse)
async def update_any_event(
    event_id: int,
    event_update: EventUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update any user's event (admin only)."""
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    updated_event = crud.update_event(db, event_id, event_update)
    return crud.get_event(db, updated_event.id)

@router.delete("/schedule/{event_id}")
async def delete_any_event(
    event_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete any user's event (admin only)."""
    success = crud.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted successfully"}
