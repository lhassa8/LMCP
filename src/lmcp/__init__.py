"""
LMCP - Lightweight Model Context Protocol

A powerful yet easy-to-use Python wrapper for the Model Context Protocol (MCP).
"""

from .client import Client, connect
from .server import Server, server, tool, resource, prompt, run_server
from .exceptions import LMCPError, ConnectionError, ServerError, ValidationError
from .types import ToolResult, ResourceResult, PromptResult
from .advanced import Pipeline, quick_connect, parallel_execute, managed_servers

__version__ = "0.1.0"
__author__ = "lhassa8"
__email__ = "lhassa8@users.noreply.github.com"

__all__ = [
    # Core functionality
    "Client",
    "Server",
    "connect",
    "server",
    "tool",
    "resource",
    "prompt",
    "run_server",
    
    # Advanced features
    "Pipeline",
    "quick_connect",
    "parallel_execute", 
    "managed_servers",
    
    # Exceptions
    "LMCPError",
    "ConnectionError",
    "ServerError",
    "ValidationError",
    
    # Types
    "ToolResult",
    "ResourceResult", 
    "PromptResult",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
]