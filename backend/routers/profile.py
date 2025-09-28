from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime

from database import get_db
from auth import get_current_user, get_password_hash, verify_password
from models import User
from schemas import UserPublic, UpdateUserRequest
from pydantic import BaseModel

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    class_name: Optional[str] = None
    grade: Optional[str] = None

class UpdateAvatarRequest(BaseModel):
    avatar_url: str

@router.get("/", response_model=UserPublic)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的个人信息"""
    return current_user

@router.put("/", response_model=UserPublic)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新个人信息"""
    update_data = profile_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证当前密码
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="当前密码不正确"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "密码修改成功"}

@router.post("/avatar")
async def update_avatar(
    avatar_data: UpdateAvatarRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新头像"""
    # 这里可以添加URL验证逻辑
    current_user.avatar_url = avatar_data.avatar_url
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "头像更新成功", "avatar_url": current_user.avatar_url}

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传头像文件"""
    # 验证文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="只支持图片文件"
        )
    
    # 验证文件大小 (2MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 2 * 1024 * 1024:  # 2MB
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过2MB"
        )
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}{file_extension}"
    
    # 创建上传目录
    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # 更新用户头像URL
    avatar_url = f"/uploads/avatars/{unique_filename}"
    current_user.avatar_url = avatar_url
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "头像上传成功", "avatar_url": avatar_url}

@router.get("/statistics")
async def get_profile_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户统计信息"""
    from models import Schedule, Event
    
    # 统计课表数量
    schedule_count = db.query(Schedule).filter(Schedule.owner_id == current_user.id).count()
    
    # 统计事件数量
    event_count = db.query(Event).join(Schedule).filter(Schedule.owner_id == current_user.id).count()
    
    return {
        "schedule_count": schedule_count,
        "event_count": event_count,
        "join_date": current_user.created_at.isoformat() if current_user.created_at else None
    }
