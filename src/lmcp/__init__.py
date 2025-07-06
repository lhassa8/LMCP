"""
LMCP - Lightweight Model Context Protocol

MCP Client for discovering and using existing MCP servers.
"""

from .simple_client import SimpleMCP
from .exceptions import LMCPError

__version__ = "0.1.0"
__author__ = "lhassa8"
__email__ = "lhassa8@users.noreply.github.com"

__all__ = [
    # Core functionality
    "SimpleMCP",
    
    # Exceptions
    "LMCPError",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
]