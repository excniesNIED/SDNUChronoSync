from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import get_db
from schemas import EventCreate, EventUpdate, EventResponse
from auth import get_current_user
from models import User
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
    db_event = crud.create_event(db, event, current_user.id)
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
    
    if db_event.owner_id != current_user.id:
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
    
    if db_event.owner_id != current_user.id:
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
