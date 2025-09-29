from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models import Base, User
from auth import get_password_hash
from routers import auth, schedule, team, admin, import_route, profile, schedules, admin_settings
from config import get_config
import uvicorn
import os

# Initialize database with default admin user
def init_db():
    """Initialize database with default admin user."""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            # Create default admin user
            default_admin = User(
                student_id="admin",
                hashed_password=get_password_hash("admin123"),  # Change this in production!
                full_name="系统管理员",
                class_name="管理员",
                grade="2024",
                role="admin"
            )
            db.add(default_admin)
            db.commit()
            print("Default admin user created:")
            print("Student ID: admin")
            print("Password: admin123")
            print("Please change the password after first login!")
        
        # Create some sample users for testing
        sample_users = [
            {
                "student_id": "202311001145",
                "password": "password123",
                "full_name": "黄浩二",
                "class_name": "计工本2303",
                "grade": "2023",
                "role": "user"
            }
        ]
        
        for user_data in sample_users:
            existing_user = db.query(User).filter(User.student_id == user_data["student_id"]).first()
            if not existing_user:
                new_user = User(
                    student_id=user_data["student_id"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    class_name=user_data["class_name"],
                    grade=user_data["grade"],
                    role=user_data["role"]
                )
                db.add(new_user)
        
        db.commit()
        print("Sample users created successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    pass

# Initialize FastAPI app
app = FastAPI(
    title="Schedule Management API",
    description="A comprehensive multi-user schedule and calendar management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4321", "http://127.0.0.1:3000", "http://127.0.0.1:4321"],  # Astro dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(schedule.router)
app.include_router(schedules.router)
app.include_router(team.router, prefix="/api")
app.include_router(admin.router)
app.include_router(admin_settings.router)
app.include_router(import_route.router)
app.include_router(profile.router)

# Setup static file serving for local avatars
config = get_config()
if config.storage_provider == "local":
    upload_path = config.get('storage.local.upload_path', 'uploads/avatars')
    base_url = config.get('storage.local.base_url', '/static/avatars')
    
    # Ensure upload directory exists
    os.makedirs(upload_path, exist_ok=True)
    
    # Mount static files
    app.mount(base_url, StaticFiles(directory=upload_path), name="avatars")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Schedule Management API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )