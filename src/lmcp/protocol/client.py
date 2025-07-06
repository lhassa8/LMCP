"""
MCP Protocol Client

Implements the client side of the MCP protocol.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, Callable, Awaitable

from ..connection import Connection
from ..types import ServerInfo, ToolInfo, ResourceInfo, PromptInfo
from ..exceptions import LMCPError, ConnectionError, ServerError, TimeoutError
from .messages import (
    MCPRequest, MCPResponse, MCPNotification,
    InitializeRequest, InitializeResponse,
    ListToolsRequest, ListToolsResponse,
    CallToolRequest, CallToolResponse,
    ListResourcesRequest, ListResourcesResponse,
    ReadResourceRequest, ReadResourceResponse,
    ListPromptsRequest, ListPromptsResponse,
    GetPromptRequest, GetPromptResponse,
    PingRequest, PongResponse
)

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP protocol client implementation."""
    
    def __init__(self, connection: Connection):
        self.connection = connection
        self._initialized = False
        self._server_info: Optional[ServerInfo] = None
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._notification_handlers: Dict[str, Callable] = {}
        self._receive_task: Optional[asyncio.Task] = None
        self._client_info = {
            "name": "lmcp",
            "version": "0.1.0"
        }
    
    async def initialize(self) -> ServerInfo:
        """Initialize the MCP session."""
        if self._initialized:
            return self._server_info
        
        try:
            # Start receiving messages BEFORE sending any requests
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            # Send initialize request
            request = InitializeRequest(
                id=self._generate_id(),
                params={
                    "protocolVersion": "2024-11-05",
                    "clientInfo": self._client_info,
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    }
                }
            )
            
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Initialization failed: {response.error}")
            
            # Parse server info
            result = response.result or {}
            self._server_info = ServerInfo(
                name=result.get("serverInfo", {}).get("name", "Unknown"),
                version=result.get("serverInfo", {}).get("version", "Unknown"),
                description=result.get("serverInfo", {}).get("description"),
                capabilities=result.get("capabilities", {})
            )
            
            # Send initialized notification
            await self._send_notification(MCPNotification(
                method="notifications/initialized"
            ))
            
            self._initialized = True
            logger.info(f"MCP client initialized with server: {self._server_info.name}")
            
            return self._server_info
            
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            raise ConnectionError(f"Failed to initialize MCP session: {e}")
    
    async def close(self) -> None:
        """Close the MCP session."""
        if not self._initialized:
            return
        
        try:
            # Cancel receive task
            if self._receive_task:
                self._receive_task.cancel()
                try:
                    await self._receive_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel pending requests
            for future in self._pending_requests.values():
                if not future.done():
                    future.cancel()
            
            self._pending_requests.clear()
            self._initialized = False
            
            logger.info("MCP client closed")
            
        except Exception as e:
            logger.error(f"Error closing MCP client: {e}")
    
    async def get_server_info(self) -> ServerInfo:
        """Get server information."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        return self._server_info
    
    async def list_tools(self) -> List[ToolInfo]:
        """List available tools."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        
        try:
            request = ListToolsRequest(id=self._generate_id())
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Failed to list tools: {response.error}")
            
            tools_data = response.result.get("tools", [])
            return [
                ToolInfo(
                    name=tool.get("name", ""),
                    description=tool.get("description"),
                    input_schema=tool.get("inputSchema", {}),
                    output_schema=tool.get("outputSchema", {})
                )
                for tool in tools_data
            ]
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise ServerError(f"Failed to list tools: {e}")
    
    async def call_tool(self, name: str, *args, **kwargs) -> Any:
        """Call a tool."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        
        try:
            # Prepare arguments
            arguments = {}
            if args:
                arguments.update({f"arg{i}": arg for i, arg in enumerate(args)})
            if kwargs:
                arguments.update(kwargs)
            
            request = CallToolRequest(
                id=self._generate_id(),
                params={
                    "name": name,
                    "arguments": arguments
                }
            )
            
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Tool call failed: {response.error}")
            
            return response.result.get("content", [])
            
        except Exception as e:
            logger.error(f"Failed to call tool '{name}': {e}")
            raise ServerError(f"Failed to call tool '{name}': {e}")
    
    async def list_resources(self) -> List[ResourceInfo]:
        """List available resources."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        
        try:
            request = ListResourcesRequest(id=self._generate_id())
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Failed to list resources: {response.error}")
            
            resources_data = response.result.get("resources", [])
            return [
                ResourceInfo(
                    uri=resource.get("uri", ""),
                    name=resource.get("name"),
                    description=resource.get("description"),
                    mime_type=resource.get("mimeType")
                )
                for resource in resources_data
            ]
            
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            raise ServerError(f"Failed to list resources: {e}")
    
    async def get_resource(self, uri: str) -> Any:
        """Get a resource."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        
        try:
            request = ReadResourceRequest(
                id=self._generate_id(),
                params={"uri": uri}
            )
            
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Failed to get resource: {response.error}")
            
            return response.result.get("contents", [])
            
        except Exception as e:
            logger.error(f"Failed to get resource '{uri}': {e}")
            raise ServerError(f"Failed to get resource '{uri}': {e}")
    
    async def list_prompts(self) -> List[PromptInfo]:
        """List available prompts."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        
        try:
            request = ListPromptsRequest(id=self._generate_id())
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Failed to list prompts: {response.error}")
            
            prompts_data = response.result.get("prompts", [])
            return [
                PromptInfo(
                    name=prompt.get("name", ""),
                    description=prompt.get("description"),
                    arguments=prompt.get("arguments", [])
                )
                for prompt in prompts_data
            ]
            
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            raise ServerError(f"Failed to list prompts: {e}")
    
    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Get a prompt."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        
        try:
            request = GetPromptRequest(
                id=self._generate_id(),
                params={
                    "name": name,
                    "arguments": arguments
                }
            )
            
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Failed to get prompt: {response.error}")
            
            return response.result.get("messages", [])
            
        except Exception as e:
            logger.error(f"Failed to get prompt '{name}': {e}")
            raise ServerError(f"Failed to get prompt '{name}': {e}")
    
    async def ping(self) -> None:
        """Send a ping to the server."""
        if not self._initialized:
            raise ConnectionError("MCP client not initialized")
        
        try:
            request = PingRequest(id=self._generate_id())
            response = await self._send_request(request)
            
            if response.error:
                raise ServerError(f"Ping failed: {response.error}")
            
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            raise ServerError(f"Ping failed: {e}")
    
    async def _send_request(self, request: MCPRequest) -> MCPResponse:
        """Send a request and wait for response."""
        try:
            # Create future for response
            future = asyncio.Future()
            self._pending_requests[str(request.id)] = future
            
            # Send request
            await self.connection.send(request.model_dump())
            
            # Wait for response
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(str(request.id), None)
            raise TimeoutError(f"Request {request.id} timed out")
        except Exception as e:
            self._pending_requests.pop(str(request.id), None)
            raise ConnectionError(f"Failed to send request: {e}")
    
    async def _send_notification(self, notification: MCPNotification) -> None:
        """Send a notification."""
        try:
            await self.connection.send(notification.model_dump())
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            raise ConnectionError(f"Failed to send notification: {e}")
    
    async def _receive_loop(self) -> None:
        """Receive and handle messages."""
        while True:
            try:
                message = await self.connection.receive()
                await self._handle_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                # Continue receiving unless it's a critical error
                if isinstance(e, ConnectionError):
                    break
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle a received message."""
        try:
            # Check if it's a response
            if "id" in message and ("result" in message or "error" in message):
                response_id = str(message["id"])
                future = self._pending_requests.pop(response_id, None)
                if future and not future.done():
                    response = MCPResponse(**message)
                    future.set_result(response)
            
            # Check if it's a notification
            elif "method" in message and "id" not in message:
                notification = MCPNotification(**message)
                await self._handle_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to handle message: {e}")
    
    async def _handle_notification(self, notification: MCPNotification) -> None:
        """Handle a notification."""
        handler = self._notification_handlers.get(notification.method)
        if handler:
            try:
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
        else:
            logger.debug(f"No handler for notification: {notification.method}")
    
    def register_notification_handler(self, method: str, handler: Callable) -> None:
        """Register a notification handler."""
        self._notification_handlers[method] = handler
    
    def _generate_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())