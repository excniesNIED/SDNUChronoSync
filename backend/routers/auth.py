from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from schemas import Token, UserResponse, LoginRequest, RegisterRequest
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from models import User
import crud

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/token", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint."""
    user = authenticate_user(db, login_data.student_id, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect student ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.student_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """User registration endpoint."""
    # Check if user already exists
    existing_user = crud.get_user_by_student_id(db, register_data.student_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(register_data.password)
    user_data = {
        "student_id": register_data.student_id,
        "hashed_password": hashed_password,
        "full_name": register_data.full_name,
        "class_name": register_data.class_name,
        "grade": register_data.grade,
        "role": "user"
    }
    
    user = crud.create_user(db, user_data)
    return user

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
