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
            # Use longer timeout and add user agent for OpenList compatibility
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "SDNUChronoSync/1.0"
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                print(f"🔍 Sending login request with headers: {headers}")
                response = await client.post(login_url, json=login_data, headers=headers)
                
                print(f"🔍 Login response status: {response.status_code}")
                print(f"🔍 Login response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    error_detail = f"Alist login failed: HTTP {response.status_code}\nResponse: {response.text[:500]}..."
                    print(f"❌ {error_detail}")
                    raise HTTPException(
                        status_code=500,
                        detail=error_detail
                    )
                
                # Check content type to ensure we got JSON
                content_type = response.headers.get('content-type', '').lower()
                if 'application/json' not in content_type:
                    print(f"⚠️ Unexpected content type: {content_type}")
                    print(f"⚠️ Response content: {response.text[:500]}...")
                
                try:
                    result = response.json()
                    print(f"🔍 Login successful, extracting token...")
                    print(f"🔍 Login response data: {result}")
                except ValueError as e:
                    print(f"❌ Failed to parse login response as JSON: {e}")
                    print(f"❌ Raw response: {response.text}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid JSON response from Alist login: {response.text[:200]}..."
                    )
                
                if result.get('code') != 200:
                    error_msg = result.get('message', 'Login failed')
                    print(f"❌ Login API error: {error_msg}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Alist login error: {error_msg}\nFull response: {result}"
                    )
                
                # Extract token from response - handle different response formats
                token_data = result.get('data', {})
                token = token_data.get('token')
                
                # Some versions might return token directly in data
                if not token and isinstance(token_data, str):
                    token = token_data
                
                if not token:
                    print(f"❌ Token not found in response: {result}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to get token from login response"
                    )
                
                print(f"✅ Fresh token obtained: {token[:20]}...")
                return token
                
        except httpx.HTTPError as e:
            print(f"❌ Login network error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Login network error: {str(e)}")
    
    async def _verify_token(self, token: str) -> bool:
        """Verify if a token is still valid by making a test API call."""
        try:
            # Use the /api/me endpoint to verify token (common in Alist/OpenList)
            verify_url = f"{self.url.rstrip('/')}/api/me"
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "SDNUChronoSync/1.0"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(verify_url, headers=headers)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get('code') == 200:
                            print("✅ Token verification successful")
                            return True
                    except ValueError:
                        pass
                
                print(f"⚠️ Token verification failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Token verification error: {e}")
            return False

    async def _get_cached_or_fresh_token(self, force_refresh: bool = False) -> str:
        """Get token with caching logic."""
        # If static token is configured, use it (but verify first)
        if self.token:
            if force_refresh or not await self._verify_token(self.token):
                print("⚠️ Static token appears invalid, but continuing with configured token")
            return self.token
        
        # Check if we need to force refresh
        if force_refresh:
            print("🔍 Force refresh requested, getting fresh token")
            token = await self._login_and_get_token()
            # Cache the fresh token
            import time
            self._cached_token = token
            self._token_expires_at = time.time() + 25 * 60  # 25 minutes (shorter cache)
            return token
        
        # Check if we have a cached token that's still valid
        if self._cached_token and self._token_expires_at:
            import time
            current_time = time.time()
            # Add 5 minute buffer to avoid edge cases
            if current_time < (self._token_expires_at - 5 * 60):
                print(f"🔍 Using cached token (expires in {int((self._token_expires_at - current_time) / 60)} minutes)")
                # Optionally verify the cached token
                if not await self._verify_token(self._cached_token):
                    print("⚠️ Cached token verification failed, getting fresh token")
                    token = await self._login_and_get_token()
                    self._cached_token = token
                    self._token_expires_at = time.time() + 25 * 60
                    return token
                return self._cached_token
            else:
                print("🔍 Cached token expired or about to expire, getting fresh token")
        
        # Get fresh token and cache it
        token = await self._login_and_get_token()
        import time
        self._cached_token = token
        self._token_expires_at = time.time() + 25 * 60  # 25 minutes
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
        """Upload file to Alist/OpenList storage with enhanced retry and method fallback."""
        if not filename:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename or '')[1] or '.jpg'
            filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Store original file content to avoid multiple reads
        original_content = await file.read()
        
        UPLOAD_AUTH_RETRY_LIMIT_TIMES = 3
        retry_times = 0
        
        while retry_times <= UPLOAD_AUTH_RETRY_LIMIT_TIMES:
            try:
                if retry_times == 0:
                    print(f"🔍 Starting OpenList/Alist upload for file: {filename}")
                else:
                    print(f"🔍 Upload retry #{retry_times} for file: {filename}")
                
                print(f"🔍 Alist config - URL: {self.url}, Version: {self.version}")
                print(f"🔍 Upload path: {self.upload_path}")
                
                # Get auth token (force refresh on retries)
                if retry_times > 0:
                    print("🔄 Forcing token refresh for retry...")
                    self._cached_token = None
                    self._token_expires_at = None
                
                auth_token = await self._get_auth_token()
                print(f"🔍 Auth token obtained: {auth_token[:20]}..." if auth_token else "❌ No auth token")
                
                # Construct paths - handle both relative and absolute paths
                clean_path = self.upload_path.strip('/')
                if clean_path:
                    full_path = f"/{clean_path}/{filename}"
                    parent_path = f"/{clean_path}"
                else:
                    full_path = f"/{filename}"
                    parent_path = "/"
                
                print(f"🔍 Full path: {full_path}")
                print(f"🔍 Parent path: {parent_path}")
                
                # Try different upload methods in order of preference
                upload_success = False
                access_url = None
                
                # Common headers for all requests
                common_headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "User-Agent": "SDNUChronoSync/1.0",
                    "Accept": "application/json",
                    "Cache-Control": "no-cache"
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Method 1: POST to /api/fs/form (recommended for OpenList/newer Alist)
                    try:
                        print("🔍 Trying Method 1: POST to /api/fs/form")
                        form_url = f"{self.url.rstrip('/')}/api/fs/form"
                        
                        headers = common_headers.copy()
                        # Don't set Content-Type for multipart, let httpx handle it
                        
                        files = {"file": (filename, original_content, "application/octet-stream")}
                        data = {"path": parent_path}
                        
                        print(f"🔍 POST form URL: {form_url}")
                        print(f"🔍 Form data: {data}")
                        print(f"🔍 Form headers: {dict(headers)}")
                        
                        response = await client.post(form_url, headers=headers, files=files, data=data)
                        print(f"🔍 POST form response: {response.status_code}")
                        print(f"🔍 Response headers: {dict(response.headers)}")
                        print(f"🔍 Response content: {response.text[:500]}...")
                        
                        # Check if we got JSON response
                        try:
                            result = response.json()
                            print(f"🔍 POST form JSON response: {result}")
                            
                            if response.status_code == 200 and result.get('code') == 200:
                                print("✅ POST form upload successful!")
                                upload_success = True
                            elif result.get('code') == 401:
                                print("🔄 POST form auth failed, will try other methods")
                            else:
                                print(f"⚠️ POST form failed: {result.get('message', 'Unknown error')}")
                                
                        except ValueError:
                            # Not JSON response - check if it's HTML (indicating success)
                            if response.status_code == 200 and 'html' in response.text.lower():
                                print("✅ POST form upload successful (HTML response indicates redirect to file browser)")
                                upload_success = True
                            else:
                                print(f"⚠️ POST form non-JSON response: {response.text[:200]}...")
                    
                    except Exception as e:
                        print(f"⚠️ POST form method failed: {e}")
                    
                    # Method 2: PUT to /api/fs/put with File-Path header
                    if not upload_success:
                        try:
                            print("🔍 Trying Method 2: PUT to /api/fs/put")
                            put_url = f"{self.url.rstrip('/')}/api/fs/put"
                            
                            headers = common_headers.copy()
                            headers.update({
                                "File-Path": full_path,
                                "Content-Type": "application/octet-stream",
                                "Content-Length": str(len(original_content))
                            })
                            
                            print(f"🔍 PUT URL: {put_url}")
                            print(f"🔍 PUT headers: {dict(headers)}")
                            
                            response = await client.put(put_url, headers=headers, content=original_content)
                            print(f"🔍 PUT response: {response.status_code}")
                            print(f"🔍 Response content: {response.text[:500]}...")
                            
                            try:
                                result = response.json()
                                print(f"🔍 PUT JSON response: {result}")
                                
                                if response.status_code == 200 and result.get('code') == 200:
                                    print("✅ PUT upload successful!")
                                    upload_success = True
                                elif result.get('code') == 401:
                                    print("🔄 PUT auth failed")
                                else:
                                    print(f"⚠️ PUT failed: {result.get('message', 'Unknown error')}")
                                    
                            except ValueError:
                                print(f"⚠️ PUT non-JSON response: {response.text[:200]}...")
                        
                        except Exception as e:
                            print(f"⚠️ PUT method failed: {e}")
                    
                    # Method 3: POST with multipart/form-data and different endpoint
                    if not upload_success:
                        try:
                            print("🔍 Trying Method 3: POST multipart upload")
                            # Try common alternative endpoints
                            alt_endpoints = [
                                "/api/fs/upload",
                                "/api/admin/fs/form", 
                                "/api/public/fs/form"
                            ]
                            
                            for endpoint in alt_endpoints:
                                upload_url = f"{self.url.rstrip('')}{endpoint}"
                                print(f"🔍 Trying endpoint: {upload_url}")
                                
                                headers = common_headers.copy()
                                # Remove Accept header for some endpoints that might not like it
                                if "/admin/" in endpoint or "/public/" in endpoint:
                                    headers.pop("Accept", None)
                                
                                files = {"file": (filename, original_content, "application/octet-stream")}
                                data = {"path": parent_path}
                                
                                print(f"🔍 {endpoint} headers: {dict(headers)}")
                                
                                try:
                                    response = await client.post(upload_url, headers=headers, files=files, data=data)
                                    print(f"🔍 {endpoint} response: {response.status_code}")
                                    print(f"🔍 {endpoint} response content: {response.text[:300]}...")
                                    
                                    if response.status_code in [200, 201]:
                                        try:
                                            result = response.json()
                                            if result.get('code') in [200, None]:
                                                print(f"✅ Upload successful via {endpoint}!")
                                                upload_success = True
                                                break
                                        except ValueError:
                                            # Some endpoints return HTML or plain text on success
                                            if response.status_code in [200, 201]:
                                                print(f"✅ Upload successful via {endpoint} (non-JSON response)!")
                                                upload_success = True
                                                break
                                
                                except Exception as e:
                                    print(f"⚠️ {endpoint} failed: {e}")
                                    continue
                            
                            # If all alternative endpoints failed, we might need to break
                            if not upload_success:
                                print("⚠️ All alternative endpoints failed")
                        
                        except Exception as e:
                            print(f"⚠️ Alternative methods failed: {e}")
                
                # If upload was successful, generate access URL
                if upload_success:
                    try:
                        await self._refresh_directory(client, auth_token, self.upload_path)
                    except Exception as e:
                        print(f"⚠️ Directory refresh failed (non-critical): {e}")
                    
                    access_url = self._get_access_url(filename)
                    print(f"✅ Access URL: {access_url}")
                    return access_url
                
                # If all methods failed, check if it's an auth issue and retry
                if retry_times < UPLOAD_AUTH_RETRY_LIMIT_TIMES:
                    print(f"🔄 All upload methods failed, retrying ({retry_times + 1}/{UPLOAD_AUTH_RETRY_LIMIT_TIMES})")
                    retry_times += 1
                    continue
                else:
                    error_detail = f"OpenList upload failed after {retry_times + 1} attempts:\nAll upload methods (POST form, PUT, alternative endpoints) failed\nURL: {self.url}\nPath: {full_path}"
                    print(f"❌ {error_detail}")
                    raise HTTPException(status_code=500, detail=error_detail)
                        
            except HTTPException:
                # Don't retry HTTPExceptions
                raise
            except Exception as e:
                print(f"❌ Unexpected error on attempt {retry_times + 1}: {e}")
                if retry_times >= UPLOAD_AUTH_RETRY_LIMIT_TIMES:
                    import traceback
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail=f"Upload failed after {retry_times + 1} attempts: {str(e)}")
                retry_times += 1
                continue
        
        # Should not reach here, but just in case
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
