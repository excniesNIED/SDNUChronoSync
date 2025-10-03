from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - allow override via environment variable for containerized deployments
# For SQLite absolute paths, use the 4-slash form: sqlite:////absolute/path/to.db
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./schedule_app.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
