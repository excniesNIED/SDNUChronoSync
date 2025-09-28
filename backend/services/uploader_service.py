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
    """Alist storage uploader with support for both token and username/password auth."""
    
    def __init__(self):
        self.config = get_config()
        self.version = self.config.get('storage.alist.version', 3)
        self.url = self.config.get('storage.alist.url', '')
        self.upload_path = self.config.get('storage.alist.upload_path', 'assets')
        
        # Auth configuration
        self.token = self.config.get('storage.alist.token', '')
        self.username = self.config.get('storage.alist.username', '')
        self.password = self.config.get('storage.alist.password', '')
        
        # Access configuration
        self.access_path = self.config.get('storage.alist.access_path', '')
        self.access_domain = self.config.get('storage.alist.access_domain', '')
        self.filename_template = self.config.get('storage.alist.filename_template', '')
        
        if not self.url:
            raise ValueError("Alist URL must be configured")
        
        # At least one auth method must be provided
        if not self.token and not (self.username and self.password):
            raise ValueError("Either token or username/password must be configured")
        
        # Cache for dynamic token (when using username/password auth)
        self._cached_token = None
        self._token_expires_at = None
    
    async def _get_auth_token(self) -> str:
        """Get authentication token, either from config or by login."""
        # If static token is configured, use it
        if self.token:
            return self.token
        
        # Check if we have a cached token that's still valid
        if self._cached_token and self._token_expires_at:
            import time
            current_time = time.time()
            # Add 5 minute buffer to avoid edge cases
            if current_time < (self._token_expires_at - 5 * 60):
                print(f"🔍 Using cached token (expires in {int((self._token_expires_at - current_time) / 60)} minutes)")
                return self._cached_token
            else:
                print("🔍 Cached token expired or about to expire, getting fresh token")
        
        # Login with username/password to get token
        if not (self.username and self.password):
            raise ValueError("No valid authentication method available")
        
        return await self._login_and_get_token()
    
    async def _login_and_get_token(self) -> str:
        """Login with username/password and get token."""
        login_url = f"{self.url.rstrip('/')}/api/auth/login"
        
        print(f"🔍 Logging in to Alist at: {login_url}")
        print(f"🔍 Username: {self.username}")
        print(f"🔍 Version: {self.version}")
        
        # Different payload for different versions
        if self.version == 2:
            login_data = {
                "username": self.username,
                "password": self.password
            }
        else:  # version 3
            login_data = {
                "username": self.username,
                "password": self.password,
                "opt_code": ""
            }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                print(f"🔍 Sending login request with data: {login_data}")
                response = await client.post(login_url, json=login_data)
                
                print(f"🔍 Login response status: {response.status_code}")
                print(f"🔍 Login response content: {response.text}")
                
                if response.status_code != 200:
                    error_detail = f"Alist login failed: HTTP {response.status_code}\nResponse: {response.text}"
                    print(f"❌ {error_detail}")
                    raise HTTPException(
                        status_code=500,
                        detail=error_detail
                    )
                
                result = response.json()
                print(f"🔍 Login JSON response: {result}")
                if result.get('code') != 200:
                    error_msg = result.get('message', 'Login failed')
                    print(f"❌ Login API error: {error_msg}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Alist login error: {error_msg}\nFull response: {result}"
                    )
                
                # Extract token from response
                token_data = result.get('data', {})
                if self.version == 2:
                    token = token_data.get('token')
                else:  # version 3
                    token = token_data.get('token')
                
                if not token:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to get token from login response"
                    )
                
                # Cache the token (shorter expiry to avoid invalidation issues)
                import time
                self._cached_token = token
                # Use shorter cache time to avoid token invalidation issues
                self._token_expires_at = time.time() + 30 * 60  # 30 minutes instead of 24 hours
                
                print(f"✅ Token cached for 30 minutes")
                return token
                
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Login network error: {str(e)}")
    
    def _apply_filename_template(self, filename: str) -> str:
        """Apply filename template if configured."""
        if not self.filename_template:
            return filename
        
        # Extract name and extension
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            template_name = self.filename_template.replace('${fileName}', name)
            return f"{template_name}.{ext}"
        else:
            return self.filename_template.replace('${fileName}', filename)
    
    def _get_access_url(self, filename: str) -> str:
        """Generate access URL based on configuration."""
        # Apply filename template if configured
        display_filename = self._apply_filename_template(filename)
        
        # Determine base URL
        base_url = self.access_domain or self.url
        
        # Determine access path
        if self.access_path:
            full_path = f"/{self.access_path.strip('/')}/{display_filename}"
        else:
            # Default: 'd/' + upload_path
            full_path = f"/d/{self.upload_path.strip('/')}/{display_filename}"
        
        return f"{base_url.rstrip('')}{full_path}"
    
    async def upload(self, file: UploadFile, filename: Optional[str] = None) -> str:
        """Upload file to Alist storage."""
        if not filename:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename or '')[1] or '.jpg'
            filename = f"{uuid.uuid4().hex}{file_extension}"
        
        try:
            print(f"🔍 Starting Alist upload for file: {filename}")
            print(f"🔍 Alist config - URL: {self.url}, Version: {self.version}")
            print(f"🔍 Upload path: {self.upload_path}")
            
            # Get auth token
            auth_token = await self._get_auth_token()
            print(f"🔍 Auth token obtained: {auth_token[:20]}..." if auth_token else "❌ No auth token")
            
            # Construct upload URL and path
            if self.version == 2:
                upload_url = f"{self.url.rstrip('/')}/api/fs/put"
                full_path = f"/{self.upload_path.strip('/')}/{filename}"
            else:  # version 3
                upload_url = f"{self.url.rstrip('/')}/api/fs/put"
                # Fix path construction - handle both relative and absolute paths
                clean_path = self.upload_path.strip('/')
                if clean_path:
                    full_path = f"/{clean_path}/{filename}"
                else:
                    full_path = f"/{filename}"
            
            print(f"🔍 Upload URL: {upload_url}")
            print(f"🔍 Full path: {full_path}")
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "File-Path": full_path,
                "Content-Type": "application/octet-stream"
            }
            
            print(f"🔍 Headers: {dict(headers)}")
            
            # Read file content
            content = await file.read()
            print(f"🔍 File content size: {len(content)} bytes")
            
            # Upload to Alist
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"🔍 Making PUT request to: {upload_url}")
                response = await client.put(
                    upload_url,
                    headers=headers,
                    content=content
                )
                
                print(f"🔍 Response status: {response.status_code}")
                print(f"🔍 Response headers: {dict(response.headers)}")
                print(f"🔍 Response content: {response.text[:500]}...")
                
                # Parse response first to check for auth errors
                try:
                    result = response.json()
                    print(f"🔍 JSON response: {result}")
                except ValueError as e:
                    print(f"❌ Failed to parse JSON response: {e}")
                    print(f"❌ Raw response: {response.text}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid JSON response from Alist: {response.text}"
                    )
                
                # Check for auth failure (both HTTP status and response code)
                auth_failed = (response.status_code == 401 or 
                             (response.status_code == 200 and result.get('code') == 401))
                
                if auth_failed and self._cached_token:
                    print("🔄 Token expired, retrying with fresh token...")
                    self._cached_token = None
                    self._token_expires_at = None
                    # Retry with fresh token
                    auth_token = await self._get_auth_token()
                    headers["Authorization"] = f"Bearer {auth_token}"
                    
                    # Reset file position for retry
                    file.file.seek(0)
                    content = await file.read()
                    
                    response = await client.put(
                        upload_url,
                        headers=headers,
                        content=content
                    )
                    print(f"🔄 Retry response status: {response.status_code}")
                    
                    # Parse retry response
                    try:
                        result = response.json()
                        print(f"🔍 Retry JSON response: {result}")
                    except ValueError as e:
                        print(f"❌ Failed to parse retry JSON response: {e}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Invalid JSON response from Alist on retry: {response.text}"
                        )
                
                # Check final response
                if response.status_code != 200 or result.get('code') != 200:
                    error_msg = result.get('message', 'Unknown error')
                    error_detail = f"Alist upload failed: HTTP {response.status_code}, Code: {result.get('code')}\nMessage: {error_msg}\nURL: {upload_url}\nPath: {full_path}"
                    print(f"❌ Final error: {error_detail}")
                    raise HTTPException(
                        status_code=500, 
                        detail=error_detail
                    )
                
                # Refresh the directory after successful upload (like PicGo does)
                try:
                    await self._refresh_directory(client, auth_token, self.upload_path)
                except Exception as e:
                    print(f"⚠️ Directory refresh failed (non-critical): {e}")
                    # Continue anyway as the file was uploaded successfully
            
            # Return accessible URL
            access_url = self._get_access_url(filename)
            print(f"✅ Upload successful! Access URL: {access_url}")
            return access_url
            
        except httpx.HTTPError as e:
            print(f"❌ Network error: {e}")
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
        except HTTPException:
            # Re-raise HTTPException as-is
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def _refresh_directory(self, client: httpx.AsyncClient, auth_token: str, path: str):
        """Refresh directory after upload (similar to PicGo implementation)."""
        refresh_url = f"{self.url.rstrip('/')}/api/fs/list"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        refresh_data = {
            "path": f"/{path.strip('/')}",
            "refresh": True
        }
        
        print(f"🔄 Refreshing directory: {refresh_data['path']}")
        
        try:
            response = await client.post(refresh_url, headers=headers, json=refresh_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("✅ Directory refreshed successfully")
                else:
                    print(f"⚠️ Directory refresh returned code {result.get('code')}: {result.get('message')}")
            else:
                print(f"⚠️ Directory refresh failed with HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️ Directory refresh exception: {e}")
            # Don't fail the upload for refresh issues

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
