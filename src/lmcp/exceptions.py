"""
LMCP Exception Classes

Defines the exception hierarchy for LMCP operations.
"""

from typing import Any, Optional, Dict


class LMCPError(Exception):
    """Base exception for all LMCP errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConnectionError(LMCPError):
    """Raised when connection to MCP server fails."""
    
    def __init__(self, message: str, server_uri: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.server_uri = server_uri


class ServerError(LMCPError):
    """Raised when MCP server returns an error."""
    
    def __init__(self, message: str, error_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_code = error_code


class ValidationError(LMCPError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.field = field


class TimeoutError(LMCPError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str, timeout: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.timeout = timeout


class AuthenticationError(LMCPError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(LMCPError):
    """Raised when authorization fails."""
    pass


class ResourceNotFoundError(LMCPError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_uri: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.resource_uri = resource_uri


class ToolNotFoundError(LMCPError):
    """Raised when a requested tool is not found."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.tool_name = tool_name