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
from urllib.parse import quote

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
    
    async def _get_auth_token(self, force_refresh: bool = False) -> str:
        """Get authentication token, either from config or by login."""
        return await self._get_cached_or_fresh_token(force_refresh)
    
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
                print(f"🔍 Sending login request")
                response = await client.post(login_url, json=login_data)
                
                print(f"🔍 Login response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = f"Alist login failed: HTTP {response.status_code}\nResponse: {response.text}"
                    print(f"❌ {error_detail}")
                    raise HTTPException(
                        status_code=500,
                        detail=error_detail
                    )
                
                result = response.json()
                print(f"🔍 Login successful, extracting token...")
                if result.get('code') != 200:
                    error_msg = result.get('message', 'Login failed')
                    print(f"❌ Login API error: {error_msg}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Alist login error: {error_msg}\nFull response: {result}"
                    )
                
                # Extract token from response
                token_data = result.get('data', {})
                token = token_data.get('token')
                
                if not token:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to get token from login response"
                    )
                
                # Don't cache token when forcing refresh - let caller decide
                print(f"✅ Fresh token obtained")
                return token
                
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Login network error: {str(e)}")
    
    async def _get_cached_or_fresh_token(self, force_refresh: bool = False) -> str:
        """Get token with caching logic."""
        # If static token is configured, use it
        if self.token:
            return self.token
        
        # Check if we need to force refresh
        if force_refresh:
            print("🔍 Force refresh requested, getting fresh token")
            token = await self._login_and_get_token()
            # Cache the fresh token
            import time
            self._cached_token = token
            self._token_expires_at = time.time() + 30 * 60  # 30 minutes
            return token
        
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
        
        # Get fresh token and cache it
        token = await self._login_and_get_token()
        import time
        self._cached_token = token
        self._token_expires_at = time.time() + 30 * 60  # 30 minutes
        return token
    
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
        """Upload file to Alist storage with a simplified, robust method."""
        if not filename:
            file_extension = os.path.splitext(file.filename or '')[1] or '.jpg'
            filename = f"{uuid.uuid4().hex}{file_extension}"
        
        content = await file.read()
        
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES + 1):
            try:
                if attempt == 0:
                    print(f"🔍 Starting Alist upload for file: {filename}")
                else:
                    print(f"🔍 Upload retry #{attempt} for file: {filename}")

                print(f"🔍 Alist config - URL: {self.url}, Version: {self.version}")
                print(f"🔍 Upload path: {self.upload_path}")

                # Force token refresh on retries
                force_refresh = attempt > 0
                if force_refresh:
                    print("🔄 Forcing token refresh for retry...")

                auth_token = await self._get_cached_or_fresh_token(force_refresh=force_refresh)
                print(f"🔍 Auth token obtained: {auth_token[:20]}..." if auth_token else "❌ No auth token")

                upload_url = f"{self.url.rstrip('/')}/api/fs/put"
                full_path = f"/{self.upload_path.strip('/')}/{filename}"
                
                print(f"🔍 Upload URL: {upload_url}")
                print(f"🔍 Full path: {full_path}")
                print(f"🔍 File content size: {len(content)} bytes")

                # Some AList deployments expect raw token (no 'Bearer') and raw File-Path
                headers = {
                    "Authorization": auth_token,  # raw token
                    "File-Path": full_path,       # raw path
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(len(content)),
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                }
                
                print(f"🔍 Sending headers: {headers}")

                async with httpx.AsyncClient(timeout=60.0) as client:
                    print("🔍 Making PUT request (stream upload)...")
                    response = await client.put(upload_url, headers=headers, content=content)

                print(f"🔍 Response status: {response.status_code}")
                print(f"🔍 Response headers: {dict(response.headers)}")
                print(f"🔍 Response content: {response.text[:500]}...")

                try:
                    result = response.json()
                    print(f"🔍 JSON response: {result}")
                except ValueError:
                    # Handle non-JSON responses (like HTML pages)
                    if 200 <= response.status_code < 300:
                         print(f"✅ Upload appears successful based on status code {response.status_code}, but response was not JSON.")
                         access_url = self._get_access_url(filename)
                         print(f"✅ Access URL: {access_url}")
                         return access_url
                    else:
                        print(f"❌ Upload failed with non-JSON response. Raw response: {response.text}")
                        raise HTTPException(status_code=500, detail=f"Alist returned a non-JSON response (HTTP {response.status_code})")

                # Check for auth failure (HTTP 401 or HTTP 200 with code 401)
                is_auth_error = (response.status_code == 401 or (result.get('code') == 401))

                if is_auth_error:
                    print(f"🔄 Auth error detected: {result.get('message', 'Unauthorized')}")
                    if attempt < MAX_RETRIES:
                        continue  # Retry will be triggered by the loop
                    else:
                        raise Exception("Authentication failed after multiple retries.")

                if result.get('code') == 200:
                    print(f"✅ Upload successful after {attempt + 1} attempt(s).")

                    # After upload, try to refresh directory and fetch a direct/actual URL
                    try:
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            json_headers = {
                                "Authorization": auth_token,
                                "Content-Type": "application/json",
                                "Accept": "application/json"
                            }

                            # 1) Refresh the directory so new file becomes visible immediately
                            try:
                                list_url = f"{self.url.rstrip('/')}/api/fs/list"
                                list_payload_refresh = {
                                    "path": f"/{self.upload_path.strip('/')}",
                                    "refresh": True
                                }
                                print(f"🔄 Refreshing directory via {list_url} with payload {list_payload_refresh}")
                                list_resp = await client.post(list_url, headers=json_headers, json=list_payload_refresh)
                                print(f"🔄 Refresh HTTP {list_resp.status_code} -> {list_resp.text[:200]}")
                            except Exception as e:
                                print(f"⚠️ Directory refresh failed: {e}")

                            # 2) Try fetching file meta for the intended path
                            try:
                                get_url = f"{self.url.rstrip('/')}/api/fs/get"
                                get_payload = {"path": full_path}
                                print(f"🔍 Fetching file meta via {get_url} with payload {get_payload}")
                                get_resp = await client.post(get_url, headers=json_headers, json=get_payload)
                                print(f"🔍 /api/fs/get HTTP {get_resp.status_code} -> {get_resp.text[:300]}")
                                if get_resp.status_code == 200:
                                    meta = get_resp.json()
                                    if meta.get("code") == 200:
                                        data = meta.get("data") or {}
                                        # Use the server's actual stored name if present
                                        actual_name = data.get("name") or filename
                                        base_url = (self.access_domain or self.url).rstrip('/')
                                        access_url_actual = f"{base_url}/d/{self.upload_path.strip('/')}/{actual_name}"
                                        print(f"✅ Returning domain URL: {access_url_actual}")
                                        return access_url_actual
                            except Exception as e:
                                print(f"⚠️ Fetching raw URL failed: {e}")

                            # 3) If the server saved with original filename, find the actual stored name by listing
                            try:
                                list_payload = {
                                    "path": f"/{self.upload_path.strip('/')}",
                                    "refresh": False
                                }
                                list_resp2 = await client.post(list_url, headers=json_headers, json=list_payload)
                                if list_resp2.status_code == 200:
                                    body = list_resp2.json()
                                    entries = ((body or {}).get("data") or {}).get("content") or []
                                    # Match by size and extension, choose the newest
                                    desired_ext = (os.path.splitext(filename)[1] or "").lower()
                                    candidates = [
                                        e for e in entries
                                        if not e.get("is_dir")
                                        and int(e.get("size") or 0) == len(content)
                                        and str(e.get("name") or "").lower().endswith(desired_ext)
                                    ]
                                    # Sort by modified fields if present
                                    def _modified_key(item):
                                        return str(item.get("modified") or item.get("modified_time") or item.get("mtime") or "")
                                    candidates.sort(key=_modified_key, reverse=True)
                                    if candidates:
                                        actual_name = candidates[0].get("name")
                                        if actual_name:
                                            # Build a working access URL with actual stored name (bypass template)
                                            base_url = (self.access_domain or self.url).rstrip('/')
                                            access_url_actual = f"{base_url}/d/{self.upload_path.strip('/')}/{actual_name}"
                                            print(f"✅ Found stored file name '{actual_name}', returning: {access_url_actual}")
                                            return access_url_actual
                            except Exception as e:
                                print(f"⚠️ Listing to detect actual file name failed: {e}")
                    except Exception as e:
                        print(f"⚠️ Post-upload URL resolution failed: {e}")

                    # Fallback to configured access URL using intended filename
                    access_url = self._get_access_url(filename)
                    print(f"✅ Access URL: {access_url}")
                    return access_url
                else:
                    error_message = result.get('message', 'Unknown Alist error')
                    print(f"❌ Alist API error (code {result.get('code')}): {error_message}")
                    raise Exception(f"Alist API error: {error_message}")

            except Exception as e:
                print(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
                if attempt >= MAX_RETRIES:
                    import traceback
                    traceback.print_exc()
                    error_detail = f"Alist upload failed after {MAX_RETRIES + 1} attempts. Last error: {str(e)}"
                    raise HTTPException(status_code=500, detail=error_detail)
        
        # This part should not be reached
        raise HTTPException(status_code=500, detail="Upload failed: Maximum retries exceeded")
    
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
