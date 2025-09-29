from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import get_current_user
from models import User, Team
import crud
from schemas import (
    TeamCreate, TeamUpdate, TeamResponse, TeamMemberAdd, 
    TeamJoinRequest, UserPublic, EventResponse
)

router = APIRouter()

# Admin only endpoints
@router.get("/admin/teams", response_model=List[TeamResponse])
async def get_all_teams_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all teams. Only accessible by system admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this endpoint"
        )
    
    teams = crud.get_all_teams(db)
    return teams

# Helper function to check permissions
def check_team_admin_permission(db: Session, team_id: int, current_user: User):
    """Check if current user is team admin (creator) or system admin"""
    if current_user.role == "admin":
        return True
    return crud.is_team_creator(db, team_id, current_user.id)

def check_team_member_permission(db: Session, team_id: int, current_user: User):
    """Check if current user is team member or system admin"""
    if current_user.role == "admin":
        return True
    return crud.is_team_member(db, team_id, current_user.id)

# General team operations
@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new team. Any logged-in user can create a team."""
    db_team = crud.create_team(db, team, current_user.id)
    return db_team

@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team details. Only accessible by team members or system admin."""
    if not check_team_member_permission(db, team_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this team"
        )
    
    team = crud.get_team(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return team

# Team management operations (require admin permission)
@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_update: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update team name. Only accessible by team creator or system admin."""
    if not check_team_admin_permission(db, team_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this team"
        )
    
    team = crud.update_team(db, team_id, team_update)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return team

@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a team. Only team creator or system admin can delete."""
    if not check_team_admin_permission(db, team_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this team"
        )
    
    success = crud.delete_team(db, team_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return {"message": "Team deleted successfully"}

@router.post("/teams/{team_id}/members", status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: int,
    member_add: TeamMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a user to team by student_id. Only accessible by team creator or system admin."""
    if not check_team_admin_permission(db, team_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add members to this team"
        )
    
    # Find user by student_id
    user = crud.get_user_by_student_id(db, member_add.student_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Add user to team
    success = crud.add_team_member(db, team_id, user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add user to team"
        )
    
    return {"message": "User added to team successfully"}

@router.delete("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a user from team. Only accessible by team creator or system admin."""
    if not check_team_admin_permission(db, team_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove members from this team"
        )
    
    success = crud.remove_team_member(db, team_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove user from team"
        )

@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a team. Only accessible by team creator or system admin."""
    if not check_team_admin_permission(db, team_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this team"
        )
    
    success = crud.delete_team(db, team_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

# User team operations
@router.get("/me/teams", response_model=List[TeamResponse])
async def get_my_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all teams the current user belongs to."""
    teams = crud.get_user_teams(db, current_user.id)
    return teams

@router.post("/me/teams/join", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def join_team(
    join_request: TeamJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a team using team code."""
    team = crud.join_team_by_code(db, join_request.team_code, current_user.id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid team code"
        )
    
    return team

@router.post("/me/teams/{team_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave a team. Users can leave any team they belong to."""
    if not crud.is_team_member(db, team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this team"
        )
    
    success = crud.remove_team_member(db, team_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to leave team"
        )

# Team schedule view
@router.get("/teams/{team_id}/schedules", response_model=List[EventResponse])
async def get_team_schedules(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated schedules from all team members' active schedules."""
    if not check_team_member_permission(db, team_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this team's schedules"
        )
    
    events = crud.get_team_schedules_events(db, team_id)
    return events