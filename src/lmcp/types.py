"""
LMCP Type Definitions

Defines the core types used throughout LMCP.
"""

from typing import Any, Dict, List, Optional, Union, Literal, Protocol
from pydantic import BaseModel, Field
from datetime import datetime


class ToolResult(BaseModel):
    """Result from a tool execution."""
    content: Any
    is_error: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResourceResult(BaseModel):
    """Result from a resource fetch."""
    content: Any
    mime_type: Optional[str] = None
    uri: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromptResult(BaseModel):
    """Result from a prompt execution."""
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ServerInfo(BaseModel):
    """Information about an MCP server."""
    name: str
    version: str
    description: Optional[str] = None
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolInfo(BaseModel):
    """Information about a tool."""
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResourceInfo(BaseModel):
    """Information about a resource."""
    uri: str
    name: Optional[str] = None
    description: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromptInfo(BaseModel):
    """Information about a prompt."""
    name: str
    description: Optional[str] = None
    arguments: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConnectionConfig(BaseModel):
    """Configuration for MCP connections."""
    uri: str
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    keepalive: bool = True
    auth: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ServerConfig(BaseModel):
    """Configuration for MCP servers."""
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    host: str = "localhost"
    port: int = 8080
    transport: Literal["stdio", "http", "websocket"] = "stdio"
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LogLevel(str):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    """Log entry structure."""
    timestamp: datetime
    level: LogLevel
    message: str
    component: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    """Health status of a connection or server."""
    status: Literal["healthy", "degraded", "unhealthy"]
    last_check: datetime
    checks: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricsData(BaseModel):
    """Metrics data structure."""
    name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MiddlewareContext(BaseModel):
    """Context passed through middleware."""
    request_id: str
    operation: str
    client_info: Dict[str, Any] = Field(default_factory=dict)
    server_info: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolCallable(Protocol):
    """Protocol for tool callables."""
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class ResourceCallable(Protocol):
    """Protocol for resource callables."""
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class PromptCallable(Protocol):
    """Protocol for prompt callables."""
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...