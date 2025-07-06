"""
LMCP Utilities

Helpful utilities to make LMCP even easier to use.
"""

from .helpers import auto_detect_servers, simple_run, create_sample_server
from .templates import ServerTemplate, ToolTemplate

__all__ = [
    "auto_detect_servers",
    "simple_run", 
    "create_sample_server",
    "ServerTemplate",
    "ToolTemplate"
]