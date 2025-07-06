"""
MCP Protocol Messages

Defines the message types used in the MCP protocol.
"""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class MCPMessage(BaseModel):
    """Base class for all MCP messages."""
    jsonrpc: str = "2.0"


class MCPRequest(MCPMessage):
    """MCP request message."""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Union[str, int]


class MCPResponse(MCPMessage):
    """MCP response message."""
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPNotification(MCPMessage):
    """MCP notification message."""
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPError(BaseModel):
    """MCP error structure."""
    code: int
    message: str
    data: Optional[Any] = None


# Initialization Messages
class InitializeRequest(MCPRequest):
    """Initialize request."""
    method: Literal["initialize"] = "initialize"
    params: Dict[str, Any] = Field(default_factory=dict)


class InitializeResponse(MCPResponse):
    """Initialize response."""
    result: Dict[str, Any] = Field(default_factory=dict)


class InitializedNotification(MCPNotification):
    """Initialized notification."""
    method: Literal["initialized"] = "initialized"


# Tool Messages
class ToolInfo(BaseModel):
    """Tool information."""
    name: str
    description: Optional[str] = None
    inputSchema: Dict[str, Any] = Field(default_factory=dict)
    outputSchema: Optional[Dict[str, Any]] = None


class ListToolsRequest(MCPRequest):
    """List tools request."""
    method: Literal["tools/list"] = "tools/list"
    params: Optional[Dict[str, Any]] = None


class ListToolsResponse(MCPResponse):
    """List tools response."""
    result: Dict[str, List[ToolInfo]] = Field(default_factory=lambda: {"tools": []})


class CallToolRequest(MCPRequest):
    """Call tool request."""
    method: Literal["tools/call"] = "tools/call"
    params: Dict[str, Any] = Field(default_factory=dict)


class CallToolResponse(MCPResponse):
    """Call tool response."""
    result: Dict[str, Any] = Field(default_factory=dict)


# Resource Messages
class ResourceInfo(BaseModel):
    """Resource information."""
    uri: str
    name: Optional[str] = None
    description: Optional[str] = None
    mimeType: Optional[str] = None


class ListResourcesRequest(MCPRequest):
    """List resources request."""
    method: Literal["resources/list"] = "resources/list"
    params: Optional[Dict[str, Any]] = None


class ListResourcesResponse(MCPResponse):
    """List resources response."""
    result: Dict[str, List[ResourceInfo]] = Field(default_factory=lambda: {"resources": []})


class ReadResourceRequest(MCPRequest):
    """Read resource request."""
    method: Literal["resources/read"] = "resources/read"
    params: Dict[str, str] = Field(default_factory=dict)


class ReadResourceResponse(MCPResponse):
    """Read resource response."""
    result: Dict[str, Any] = Field(default_factory=dict)


# Prompt Messages
class PromptInfo(BaseModel):
    """Prompt information."""
    name: str
    description: Optional[str] = None
    arguments: List[Dict[str, Any]] = Field(default_factory=list)


class ListPromptsRequest(MCPRequest):
    """List prompts request."""
    method: Literal["prompts/list"] = "prompts/list"
    params: Optional[Dict[str, Any]] = None


class ListPromptsResponse(MCPResponse):
    """List prompts response."""
    result: Dict[str, List[PromptInfo]] = Field(default_factory=lambda: {"prompts": []})


class GetPromptRequest(MCPRequest):
    """Get prompt request."""
    method: Literal["prompts/get"] = "prompts/get"
    params: Dict[str, Any] = Field(default_factory=dict)


class GetPromptResponse(MCPResponse):
    """Get prompt response."""
    result: Dict[str, Any] = Field(default_factory=dict)


# Sampling Messages (for LLM completions)
class SamplingRequest(MCPRequest):
    """Sampling request."""
    method: Literal["sampling/createMessage"] = "sampling/createMessage"
    params: Dict[str, Any] = Field(default_factory=dict)


class SamplingResponse(MCPResponse):
    """Sampling response."""
    result: Dict[str, Any] = Field(default_factory=dict)


# Completion Messages
class CompletionRequest(MCPRequest):
    """Completion request."""
    method: Literal["completion/complete"] = "completion/complete"
    params: Dict[str, Any] = Field(default_factory=dict)


class CompletionResponse(MCPResponse):
    """Completion response."""
    result: Dict[str, Any] = Field(default_factory=dict)


# Logging Messages
class LoggingNotification(MCPNotification):
    """Logging notification."""
    method: Literal["notifications/message"] = "notifications/message"
    params: Dict[str, Any] = Field(default_factory=dict)


# Progress Messages
class ProgressNotification(MCPNotification):
    """Progress notification."""
    method: Literal["notifications/progress"] = "notifications/progress"
    params: Dict[str, Any] = Field(default_factory=dict)


# Resource Update Messages
class ResourceUpdatedNotification(MCPNotification):
    """Resource updated notification."""
    method: Literal["notifications/resources/updated"] = "notifications/resources/updated"
    params: Dict[str, Any] = Field(default_factory=dict)


class ResourceListChangedNotification(MCPNotification):
    """Resource list changed notification."""
    method: Literal["notifications/resources/list_changed"] = "notifications/resources/list_changed"
    params: Optional[Dict[str, Any]] = None


# Tool List Changed Messages
class ToolListChangedNotification(MCPNotification):
    """Tool list changed notification."""
    method: Literal["notifications/tools/list_changed"] = "notifications/tools/list_changed"
    params: Optional[Dict[str, Any]] = None


# Prompt List Changed Messages
class PromptListChangedNotification(MCPNotification):
    """Prompt list changed notification."""
    method: Literal["notifications/prompts/list_changed"] = "notifications/prompts/list_changed"
    params: Optional[Dict[str, Any]] = None


# Ping/Pong Messages
class PingRequest(MCPRequest):
    """Ping request."""
    method: Literal["ping"] = "ping"
    params: Optional[Dict[str, Any]] = None


class PongResponse(MCPResponse):
    """Pong response."""
    result: Dict[str, Any] = Field(default_factory=lambda: {"type": "pong"})