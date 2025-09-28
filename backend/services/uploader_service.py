"""
File upload service with support for multiple storage backends.
Supports local storage and Alist storage providers.
"""

import os
import uuid
import aiofiles
import httpx
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from fastapi import UploadFile, HTTPException
from pathlib import Path

from config import get_config

class UploaderBase(ABC):
    """Abstract base class for file uploaders."""
    
    @abstractmethod
    async def upload(self, file: UploadFile, filename: Optional[str] = None) -> str:
        """
        Upload file and return the accessible URL.
        
        Args:
            file: The uploaded file
            filename: Optional custom filename
            
        Returns:
            str: The accessible URL of the uploaded file
        """
        pass

class LocalUploader(UploaderBase):
    """Local file system uploader."""
    
    def __init__(self):
        self.config = get_config()
        self.upload_path = self.config.get('storage.local.upload_path', 'uploads/avatars')
        self.base_url = self.config.get('storage.local.base_url', '/static/avatars')
        
        # Ensure upload directory exists
        os.makedirs(self.upload_path, exist_ok=True)
    
    async def upload(self, file: UploadFile, filename: Optional[str] = None) -> str:
        """Upload file to local storage."""
        if not filename:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename or '')[1] or '.jpg'
            filename = f"{uuid.uuid4().hex}{file_extension}"
        
        file_path = os.path.join(self.upload_path, filename)
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Return accessible URL
            return f"{self.base_url}/{filename}"
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

class AlistUploader(UploaderBase):
    """Alist storage uploader."""
    
    def __init__(self):
        self.config = get_config()
        self.url = self.config.get('storage.alist.url', '')
        self.token = self.config.get('storage.alist.token', '')
        self.upload_path = self.config.get('storage.alist.upload_path', '/_imageStore')
        self.custom_url = self.config.get('storage.alist.custom_url', '')
        
        if not self.url or not self.token:
            raise ValueError("Alist URL and token must be configured")
    
    async def upload(self, file: UploadFile, filename: Optional[str] = None) -> str:
        """Upload file to Alist storage."""
        if not filename:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename or '')[1] or '.jpg'
            filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Construct upload URL
        upload_url = f"{self.url.rstrip('/')}/api/fs/put"
        full_path = f"{self.upload_path.rstrip('/')}/{filename}"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "File-Path": full_path,
            "Content-Type": "application/octet-stream"
        }
        
        try:
            # Read file content
            content = await file.read()
            
            # Upload to Alist
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    upload_url,
                    headers=headers,
                    content=content
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Alist upload failed: {response.status_code} {response.text}"
                    )
                
                result = response.json()
                if result.get('code') != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Alist upload error: {result.get('message', 'Unknown error')}"
                    )
            
            # Return accessible URL
            base_url = self.custom_url or self.url
            return f"{base_url.rstrip('/')}/d{full_path}"
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def get_uploader() -> UploaderBase:
    """
    Factory function to get the configured uploader instance.
    
    Returns:
        UploaderBase: The configured uploader instance
    """
    config = get_config()
    provider = config.storage_provider
    
    if provider == "local":
        return LocalUploader()
    elif provider == "alist":
        return AlistUploader()
    else:
        raise ValueError(f"Unknown storage provider: {provider}")

async def upload_avatar(file: UploadFile, user_id: int) -> str:
    """
    Upload user avatar with standardized filename.
    
    Args:
        file: The uploaded file
        user_id: User ID for generating filename
        
    Returns:
        str: The accessible URL of the uploaded avatar
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Validate file size (max 5MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Generate filename
    file_extension = os.path.splitext(file.filename or '')[1] or '.jpg'
    filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}{file_extension}"
    
    # Upload file
    uploader = get_uploader()
    return await uploader.upload(file, filename)
