from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserPublic, EventResponse, ScheduleFilter
from auth import get_current_user
from models import User
import crud
from datetime import datetime

router = APIRouter(prefix="/api/team", tags=["team & shared views"])

@router.get("/users", response_model=List[UserPublic])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users' public information for team filtering."""
    users = crud.get_users(db)
    return users

@router.get("/schedule/user/{user_id}", response_model=List[EventResponse])
async def get_user_schedule(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get schedule for a specific user (member lookup feature)."""
    # Check if target user exists
    target_user = crud.get_user(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    events = crud.get_user_events(db, user_id)
    return events

@router.get("/schedule/filtered", response_model=List[EventResponse])
async def get_filtered_schedule(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    user_ids: str = Query(None, description="Comma-separated user IDs, e.g., '1,5,12'"),
    class_name: str = Query(None, description="Filter by class name"),
    grade: str = Query(None, description="Filter by grade"),
    full_name_contains: str = Query(None, description="Filter by name containing text"),
    event_title_contains: str = Query(None, description="Filter by event title containing text"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Core query interface for aggregated multi-user schedule with complex filtering.
    
    This endpoint supports comprehensive filtering of events across multiple users
    based on various criteria including date range, specific users, class, grade,
    name, and event title.
    """
    
    try:
        # Parse date strings
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD format."
        )
    
    # Parse user_ids if provided
    parsed_user_ids = None
    if user_ids:
        try:
            parsed_user_ids = [int(uid.strip()) for uid in user_ids.split(",") if uid.strip()]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid user_ids format. Use comma-separated integers."
            )
    
    # Get filtered events
    events = crud.get_filtered_events(
        db=db,
        start_date=start_datetime,
        end_date=end_datetime,
        user_ids=parsed_user_ids,
        class_name=class_name,
        grade=grade,
        full_name_contains=full_name_contains,
        event_title_contains=event_title_contains
    )
    
    return events
