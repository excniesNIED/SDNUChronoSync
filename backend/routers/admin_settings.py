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

class StorageConfig(BaseModel):
    """Storage configuration model."""
    provider: str
    local: Dict[str, Any] = {}
    alist: Dict[str, Any] = {}

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
            if not alist_config.get('url') or not alist_config.get('token'):
                raise HTTPException(
                    status_code=400,
                    detail="Alist 配置需要 URL 和 token"
                )
        
        # Update configuration
        new_config = {
            "storage": {
                "provider": settings.storage.provider,
                "local": settings.storage.local,
                "alist": settings.storage.alist
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
    alist_config: Dict[str, Any],
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """测试 Alist 连接"""
    try:
        import httpx
        
        url = alist_config.get('url')
        token = alist_config.get('token')
        
        if not url or not token:
            raise HTTPException(status_code=400, detail="需要提供 URL 和 token")
        
        # Test connection to Alist
        headers = {"Authorization": f"Bearer {token}"}
        test_url = f"{url.rstrip('/')}/api/me"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(test_url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return {
                        "success": True, 
                        "message": "连接成功",
                        "user_info": result.get('data', {})
                    }
                else:
                    return {
                        "success": False,
                        "message": f"认证失败: {result.get('message', 'Unknown error')}"
                    }
            else:
                return {
                    "success": False,
                    "message": f"连接失败: HTTP {response.status_code}"
                }
                
    except httpx.TimeoutException:
        return {"success": False, "message": "连接超时"}
    except httpx.HTTPError as e:
        return {"success": False, "message": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"测试失败: {str(e)}"}
