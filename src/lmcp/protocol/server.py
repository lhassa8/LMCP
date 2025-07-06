"""
MCP Protocol Server

Implements the server side of the MCP protocol.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, Callable, Awaitable

from ..types import ServerConfig, ToolResult, ResourceResult, PromptResult, ToolInfo
from ..exceptions import LMCPError, ValidationError
from .messages import (
    MCPRequest, MCPResponse, MCPNotification, MCPError,
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


class MCPServer:
    """MCP protocol server implementation."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self._initialized = False
        self._client_info: Optional[Dict[str, Any]] = None
        self._capabilities: Dict[str, Any] = {}
        
        # Request handlers
        self._tool_handler: Optional[Callable] = None
        self._resource_handler: Optional[Callable] = None
        self._prompt_handler: Optional[Callable] = None
        
        # List handlers for getting available items
        self._tools_list_handler: Optional[Callable] = None
        self._resources_list_handler: Optional[Callable] = None
        self._prompts_list_handler: Optional[Callable] = None
        
        # Message handlers
        self._request_handlers: Dict[str, Callable] = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_list_tools,
            "tools/call": self._handle_call_tool,
            "resources/list": self._handle_list_resources,
            "resources/read": self._handle_read_resource,
            "prompts/list": self._handle_list_prompts,
            "prompts/get": self._handle_get_prompt,
            "ping": self._handle_ping
        }
        
        self._notification_handlers: Dict[str, Callable] = {
            "notifications/initialized": self._handle_initialized,
            "notifications/cancelled": self._handle_cancelled
        }
    
    async def start(self) -> None:
        """Start the MCP server."""
        if self._initialized:
            return
        
        logger.info(f"Starting MCP server: {self.config.name}")
        
        # Set up capabilities
        self._capabilities = {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True},
            **self.config.capabilities
        }
        
        # Start message processing loop
        await self._start_processing()
        
        logger.info(f"MCP server started: {self.config.name}")
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        if not self._initialized:
            return
        
        logger.info(f"Stopping MCP server: {self.config.name}")
        
        # Clean up
        self._initialized = False
        
        logger.info(f"MCP server stopped: {self.config.name}")
    
    async def register_tool_handler(self, handler: Callable[[str, Dict[str, Any]], Awaitable[ToolResult]]) -> None:
        """Register a tool handler."""
        self._tool_handler = handler
    
    async def register_resource_handler(self, handler: Callable[[str], Awaitable[ResourceResult]]) -> None:
        """Register a resource handler."""
        self._resource_handler = handler
    
    async def register_prompt_handler(self, handler: Callable[[str, Dict[str, Any]], Awaitable[PromptResult]]) -> None:
        """Register a prompt handler."""
        self._prompt_handler = handler
    
    async def register_tools_list_handler(self, handler: Callable[[], Awaitable[List[Dict[str, Any]]]]) -> None:
        """Register a tools list handler."""
        self._tools_list_handler = handler
    
    async def register_resources_list_handler(self, handler: Callable[[], Awaitable[List[Dict[str, Any]]]]) -> None:
        """Register a resources list handler."""
        self._resources_list_handler = handler
    
    async def register_prompts_list_handler(self, handler: Callable[[], Awaitable[List[Dict[str, Any]]]]) -> None:
        """Register a prompts list handler."""
        self._prompts_list_handler = handler
    
    async def _start_processing(self) -> None:
        """Start processing messages."""
        import sys
        import json
        
        self._initialized = True
        
        # For stdio transport, we need to read from stdin
        if self.config.transport == "stdio":
            # Start stdin reader task
            self._stdin_task = asyncio.create_task(self._read_stdin())
    
    async def _read_stdin(self) -> None:
        """Read and process messages from stdin."""
        import sys
        import json
        
        logger.info("Starting stdin reader...")
        
        try:
            loop = asyncio.get_event_loop()
            
            while True:
                logger.debug("Waiting for stdin input...")
                # Read a line from stdin using thread executor
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                logger.debug(f"Read line: {repr(line)}")
                
                if not line:  # EOF
                    logger.info("EOF received, stopping stdin reader")
                    break
                
                line = line.strip()
                if not line:
                    logger.debug("Empty line, continuing...")
                    continue
                
                try:
                    # Parse JSON message
                    message = json.loads(line)
                    logger.info(f"Received message: {message}")
                    
                    # Process the message
                    response = await self.handle_message(message)
                    
                    # Send response if there is one
                    if response:
                        output = json.dumps(response)
                        print(output, flush=True)
                        logger.info(f"Sent response: {output}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error reading from stdin: {e}")
            raise
    
    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle an incoming message."""
        try:
            # Check if it's a request
            if "method" in message and "id" in message:
                request = MCPRequest(**message)
                return await self._handle_request(request)
            
            # Check if it's a notification
            elif "method" in message and "id" not in message:
                notification = MCPNotification(**message)
                await self._handle_notification(notification)
                return None
            
            else:
                # Don't log unknown message types as they interfere with stdio protocol
                pass
                return None
                
        except Exception as e:
            logger.error(f"Failed to handle message: {e}")
            if "id" in message:
                return self._create_error_response(
                    message["id"],
                    -32603,  # Internal error
                    f"Internal server error: {e}"
                )
            return None
    
    async def _handle_request(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle a request and return a response."""
        handler = self._request_handlers.get(request.method)
        
        if not handler:
            return self._create_error_response(
                request.id,
                -32601,  # Method not found
                f"Method not found: {request.method}"
            )
        
        try:
            response = await handler(request)
            return response.model_dump()
        except Exception as e:
            logger.error(f"Request handler failed: {e}")
            return self._create_error_response(
                request.id,
                -32603,  # Internal error
                f"Request handler failed: {e}"
            )
    
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
    
    async def _handle_initialize(self, request: InitializeRequest) -> InitializeResponse:
        """Handle initialize request."""
        params = request.params or {}
        
        # Store client info
        self._client_info = params.get("clientInfo", {})
        
        # Return server info
        return InitializeResponse(
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": self.config.name,
                    "version": self.config.version,
                    "description": self.config.description
                },
                "capabilities": self._capabilities
            }
        )
    
    async def _handle_initialized(self, notification: MCPNotification) -> None:
        """Handle initialized notification."""
        self._initialized = True
        logger.info("MCP server initialized by client")
    
    async def _handle_list_tools(self, request: ListToolsRequest) -> ListToolsResponse:
        """Handle list tools request."""
        if not self._tools_list_handler:
            logger.warning("No tools list handler registered")
            return ListToolsResponse(
                id=request.id,
                result={"tools": []}
            )
        
        try:
            tools = await self._tools_list_handler()
            return ListToolsResponse(
                id=request.id,
                result={"tools": tools}
            )
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return ListToolsResponse(
                id=request.id,
                result={"tools": []},
                error={"code": -32603, "message": f"Failed to list tools: {e}"}
            )
    
    async def _handle_call_tool(self, request: CallToolRequest) -> CallToolResponse:
        """Handle call tool request."""
        if not self._tool_handler:
            raise ValidationError("No tool handler registered")
        
        params = request.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValidationError("Tool name is required")
        
        try:
            result = await self._tool_handler(tool_name, arguments)
            
            if result.is_error:
                return CallToolResponse(
                    id=request.id,
                    error={
                        "code": -32000,  # Server error
                        "message": result.error_message or "Tool execution failed"
                    }
                )
            
            return CallToolResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": str(result.content)
                        }
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return CallToolResponse(
                id=request.id,
                error={
                    "code": -32000,  # Server error
                    "message": f"Tool execution failed: {e}"
                }
            )
    
    async def _handle_list_resources(self, request: ListResourcesRequest) -> ListResourcesResponse:
        """Handle list resources request."""
        if not self._resources_list_handler:
            logger.warning("No resources list handler registered")
            return ListResourcesResponse(
                id=request.id,
                result={"resources": []}
            )
        
        try:
            resources = await self._resources_list_handler()
            return ListResourcesResponse(
                id=request.id,
                result={"resources": resources}
            )
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return ListResourcesResponse(
                id=request.id,
                result={"resources": []},
                error={"code": -32603, "message": f"Failed to list resources: {e}"}
            )
    
    async def _handle_read_resource(self, request: ReadResourceRequest) -> ReadResourceResponse:
        """Handle read resource request."""
        if not self._resource_handler:
            raise ValidationError("No resource handler registered")
        
        params = request.params or {}
        uri = params.get("uri")
        
        if not uri:
            raise ValidationError("Resource URI is required")
        
        try:
            result = await self._resource_handler(uri)
            
            return ReadResourceResponse(
                id=request.id,
                result={
                    "contents": [
                        {
                            "uri": result.uri,
                            "mimeType": result.mime_type or "text/plain",
                            "text": str(result.content)
                        }
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"Resource read failed: {e}")
            raise ValidationError(f"Failed to read resource: {e}")
    
    async def _handle_list_prompts(self, request: ListPromptsRequest) -> ListPromptsResponse:
        """Handle list prompts request."""
        if not self._prompts_list_handler:
            logger.warning("No prompts list handler registered")
            return ListPromptsResponse(
                id=request.id,
                result={"prompts": []}
            )
        
        try:
            prompts = await self._prompts_list_handler()
            return ListPromptsResponse(
                id=request.id,
                result={"prompts": prompts}
            )
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            return ListPromptsResponse(
                id=request.id,
                result={"prompts": []},
                error={"code": -32603, "message": f"Failed to list prompts: {e}"}
            )
    
    async def _handle_get_prompt(self, request: GetPromptRequest) -> GetPromptResponse:
        """Handle get prompt request."""
        if not self._prompt_handler:
            raise ValidationError("No prompt handler registered")
        
        params = request.params or {}
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not prompt_name:
            raise ValidationError("Prompt name is required")
        
        try:
            result = await self._prompt_handler(prompt_name, arguments)
            
            return GetPromptResponse(
                id=request.id,
                result={
                    "description": f"Generated prompt: {prompt_name}",
                    "messages": result.messages
                }
            )
            
        except Exception as e:
            logger.error(f"Prompt generation failed: {e}")
            raise ValidationError(f"Failed to generate prompt: {e}")
    
    async def _handle_ping(self, request: PingRequest) -> PongResponse:
        """Handle ping request."""
        return PongResponse(
            id=request.id,
            result={"type": "pong"}
        )
    
    async def _handle_cancelled(self, notification: MCPNotification) -> None:
        """Handle cancelled notification."""
        params = notification.params or {}
        request_id = params.get("requestId")
        reason = params.get("reason", "Request cancelled")
        
        logger.info(f"Request {request_id} was cancelled: {reason}")
    
    def _create_error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())