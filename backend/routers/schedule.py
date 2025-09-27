from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import get_db
from schemas import EventCreate, EventUpdate, EventResponse
from auth import get_current_user
from models import User, Schedule
import crud
from ics import Calendar, Event as ICSEvent
from datetime import datetime

router = APIRouter(prefix="/api/schedule", tags=["personal schedule"])

@router.get("/", response_model=List[EventResponse])
async def get_my_events(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all events for the current user."""
    events = crud.get_user_events(db, current_user.id, skip=skip, limit=limit)
    return events

@router.post("/", response_model=EventResponse)
async def create_my_event(
    event: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new event for the current user."""
    # Get or create user's default schedule
    user_schedule = db.query(Schedule).filter(Schedule.owner_id == current_user.id).first()
    
    if not user_schedule:
        # Create default schedule
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
            name="我的课表",
            owner_id=current_user.id,
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

@router.put("/{event_id}", response_model=EventResponse)
async def update_my_event(
    event_id: int,
    event_update: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an event belonging to the current user."""
    # Check if event exists and belongs to current user
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if db_event.schedule.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this event"
        )
    
    updated_event = crud.update_event(db, event_id, event_update)
    return crud.get_event(db, updated_event.id)

@router.delete("/{event_id}")
async def delete_my_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an event belonging to the current user."""
    # Check if event exists and belongs to current user
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if db_event.schedule.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this event"
        )
    
    success = crud.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted successfully"}

@router.get("/export/ics")
async def export_my_schedule_ics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export current user's schedule as ICS file."""
    events = crud.get_user_events(db, current_user.id)
    
    # Create ICS calendar
    calendar = Calendar()
    calendar.creator = f"Schedule App - {current_user.full_name}"
    
    for event in events:
        ics_event = ICSEvent()
        ics_event.name = event.title
        ics_event.begin = event.start_time
        ics_event.end = event.end_time
        ics_event.description = event.description or ""
        ics_event.location = event.location or ""
        calendar.events.add(ics_event)
    
    # Return ICS file
    ics_content = str(calendar)
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename={current_user.student_id}_schedule.ics"
        }
    )
