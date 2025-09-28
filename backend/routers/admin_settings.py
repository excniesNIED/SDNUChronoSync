"""
Admin settings API for managing system configuration.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from database import get_db
from auth import get_current_admin_user
from models import User
from config import get_config, reload_config

router = APIRouter(prefix="/api/admin", tags=["admin-settings"])

class AlistConfig(BaseModel):
    """Alist configuration model."""
    version: int = 3
    url: str = ""
    upload_path: str = "assets"
    token: str = ""
    username: str = ""
    password: str = ""
    access_path: str = ""
    access_domain: str = ""
    filename_template: str = ""

class LocalConfig(BaseModel):
    """Local storage configuration model."""
    upload_path: str = "uploads/avatars"
    base_url: str = "/static/avatars"

class StorageConfig(BaseModel):
    """Storage configuration model."""
    provider: str
    local: LocalConfig = LocalConfig()
    alist: AlistConfig = AlistConfig()

class SystemConfig(BaseModel):
    """System configuration model."""
    storage: StorageConfig

@router.get("/settings")
async def get_system_settings(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取系统配置"""
    try:
        config = get_config()
        return {
            "storage": {
                "provider": config.get('storage.provider', 'local'),
                "local": config.get('storage.local', {}),
                "alist": config.get('storage.alist', {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@router.post("/settings")
async def update_system_settings(
    settings: SystemConfig,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新系统配置"""
    try:
        config = get_config()
        
        # Validate provider
        if settings.storage.provider not in ['local', 'alist']:
            raise HTTPException(
                status_code=400, 
                detail="存储提供商必须是 'local' 或 'alist'"
            )
        
        # Validate Alist configuration if selected
        if settings.storage.provider == 'alist':
            alist_config = settings.storage.alist
            if not alist_config.url:
                raise HTTPException(
                    status_code=400,
                    detail="Alist 配置需要 URL"
                )
            
            # Check auth method
            has_token = bool(alist_config.token)
            has_username_password = bool(alist_config.username and alist_config.password)
            
            if not has_token and not has_username_password:
                raise HTTPException(
                    status_code=400,
                    detail="Alist 配置需要 Token 或者用户名密码"
                )
        
        # Update configuration
        new_config = {
            "storage": {
                "provider": settings.storage.provider,
                "local": settings.storage.local.dict(),
                "alist": settings.storage.alist.dict()
            }
        }
        
        config.update_config(new_config)
        
        # Reload configuration to apply changes
        reload_config()
        
        return {"message": "配置更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

@router.post("/settings/test-alist")
async def test_alist_connection(
    alist_config: AlistConfig,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """测试 Alist 连接"""
    try:
        import httpx
        
        if not alist_config.url:
            return {"success": False, "message": "需要提供 URL"}
        
        # Check auth method
        has_token = bool(alist_config.token)
        has_username_password = bool(alist_config.username and alist_config.password)
        
        if not has_token and not has_username_password:
            return {"success": False, "message": "需要提供 Token 或者用户名密码"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # If we have a token, test it directly
            if has_token:
                headers = {"Authorization": f"Bearer {alist_config.token}"}
                test_url = f"{alist_config.url.rstrip('/')}/api/me"
                
                response = await client.get(test_url, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        return {
                            "success": True, 
                            "message": "Token连接成功",
                            "auth_method": "token",
                            "user_info": result.get('data', {})
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Token认证失败: {result.get('message', 'Unknown error')}"
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Token连接失败: HTTP {response.status_code}"
                    }
            
            # Test username/password login
            elif has_username_password:
                login_url = f"{alist_config.url.rstrip('/')}/api/auth/login"
                
                # Different payload for different versions
                if alist_config.version == 2:
                    login_data = {
                        "username": alist_config.username,
                        "password": alist_config.password
                    }
                else:  # version 3
                    login_data = {
                        "username": alist_config.username,
                        "password": alist_config.password,
                        "opt_code": ""
                    }
                
                response = await client.post(login_url, json=login_data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        token_data = result.get('data', {})
                        token = token_data.get('token')
                        
                        if token:
                            return {
                                "success": True, 
                                "message": "用户名密码连接成功",
                                "auth_method": "username_password",
                                "user_info": token_data
                            }
                        else:
                            return {
                                "success": False,
                                "message": "登录成功但未获取到Token"
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"登录失败: {result.get('message', 'Unknown error')}"
                        }
                else:
                    return {
                        "success": False,
                        "message": f"用户名密码连接失败: HTTP {response.status_code}"
                    }
                
    except httpx.TimeoutException:
        return {"success": False, "message": "连接超时"}
    except httpx.HTTPError as e:
        return {"success": False, "message": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"测试失败: {str(e)}"}
