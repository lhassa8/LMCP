"""
Authentication Middleware

Provides authentication functionality for requests.
"""

import base64
import hashlib
import hmac
import time
from typing import Any, Dict, Optional, Callable, Awaitable

from .base import Middleware
from ..types import MiddlewareContext
from ..exceptions import AuthenticationError


class AuthMiddleware(Middleware):
    """Middleware for handling authentication."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.auth_type = self.config.get("type", "bearer")  # bearer, basic, api_key, hmac
        self.credentials = self.config.get("credentials", {})
        self.header_name = self.config.get("header_name", "Authorization")
        self.auto_refresh = self.config.get("auto_refresh", True)
        
        # Token expiration tracking
        self._token_expires_at: Optional[float] = None
        self._refresh_token: Optional[str] = None
    
    async def process_request(
        self, 
        context: MiddlewareContext, 
        request: Dict[str, Any],
        next_handler: Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Add authentication to the request."""
        # Check if token needs refresh
        if self.auto_refresh and self._needs_refresh():
            await self._refresh_token_if_needed()
        
        # Add authentication header
        auth_header = await self._get_auth_header(context, request)
        if auth_header:
            if "headers" not in request:
                request["headers"] = {}
            request["headers"][self.header_name] = auth_header
        
        # Call next handler
        return await next_handler(context, request)
    
    async def process_response(
        self, 
        context: MiddlewareContext, 
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process response and handle auth errors."""
        # Check for authentication errors
        if "error" in response:
            error = response["error"]
            if isinstance(error, dict):
                code = error.get("code")
                if code in (401, 403):  # Unauthorized or Forbidden
                    # Try to refresh token if available
                    if self.auto_refresh and self._refresh_token:
                        await self._refresh_token_if_needed()
                    else:
                        raise AuthenticationError(f"Authentication failed: {error}")
        
        return response
    
    async def _get_auth_header(self, context: MiddlewareContext, request: Dict[str, Any]) -> Optional[str]:
        """Get the authentication header value."""
        if self.auth_type == "bearer":
            return await self._get_bearer_token()
        elif self.auth_type == "basic":
            return await self._get_basic_auth()
        elif self.auth_type == "api_key":
            return await self._get_api_key()
        elif self.auth_type == "hmac":
            return await self._get_hmac_auth(request)
        else:
            return None
    
    async def _get_bearer_token(self) -> Optional[str]:
        """Get Bearer token."""
        token = self.credentials.get("token")
        if token:
            return f"Bearer {token}"
        return None
    
    async def _get_basic_auth(self) -> Optional[str]:
        """Get Basic authentication."""
        username = self.credentials.get("username")
        password = self.credentials.get("password")
        
        if username and password:
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            return f"Basic {credentials}"
        return None
    
    async def _get_api_key(self) -> Optional[str]:
        """Get API key."""
        api_key = self.credentials.get("api_key")
        if api_key:
            return api_key
        return None
    
    async def _get_hmac_auth(self, request: Dict[str, Any]) -> Optional[str]:
        """Get HMAC authentication."""
        secret = self.credentials.get("secret")
        if not secret:
            return None
        
        # Create signature
        timestamp = str(int(time.time()))
        method = request.get("method", "POST")
        path = request.get("path", "/")
        body = str(request.get("params", ""))
        
        # Create message to sign
        message = f"{method}\n{path}\n{timestamp}\n{body}"
        
        # Create HMAC signature
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"HMAC-SHA256 {timestamp}:{signature}"
    
    def _needs_refresh(self) -> bool:
        """Check if token needs refresh."""
        if not self._token_expires_at:
            return False
        
        # Refresh if token expires within 5 minutes
        return time.time() + 300 > self._token_expires_at
    
    async def _refresh_token_if_needed(self) -> None:
        """Refresh token if needed and possible."""
        if not self._refresh_token:
            return
        
        try:
            # This would typically make a request to a token refresh endpoint
            # For now, we'll just log that we would refresh
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Token refresh would be attempted here")
            
            # In a real implementation, you would:
            # 1. Make a request to the token refresh endpoint
            # 2. Update self.credentials["token"] with the new token
            # 3. Update self._token_expires_at with the new expiration time
            
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {e}")
    
    async def set_credentials(self, credentials: Dict[str, Any]) -> None:
        """Update authentication credentials."""
        self.credentials.update(credentials)
        
        # Update token expiration if provided
        if "expires_at" in credentials:
            self._token_expires_at = credentials["expires_at"]
        
        if "refresh_token" in credentials:
            self._refresh_token = credentials["refresh_token"]
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status."""
        return {
            "auth_type": self.auth_type,
            "has_credentials": bool(self.credentials),
            "token_expires_at": self._token_expires_at,
            "needs_refresh": self._needs_refresh(),
            "header_name": self.header_name
        }