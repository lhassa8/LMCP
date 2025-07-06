"""
LMCP Server Implementation

Provides decorators and utilities for creating MCP servers.
"""

import asyncio
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, get_type_hints
from functools import wraps
from datetime import datetime

from .types import (
    ToolInfo, ResourceInfo, PromptInfo, ServerConfig, ToolCallable, 
    ResourceCallable, PromptCallable, ToolResult, ResourceResult, PromptResult
)
from .exceptions import LMCPError, ValidationError
from .protocol import MCPServer

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class ToolRegistry:
    """Registry for server tools."""
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, func: Callable, description: Optional[str] = None):
        """Register a tool function."""
        # Get type hints for schema generation
        hints = get_type_hints(func)
        sig = inspect.signature(func)
        
        # Build input schema from parameters
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = hints.get(param_name, str)
            python_to_json = {
                int: "integer",
                float: "number", 
                str: "string",
                bool: "boolean",
                list: "array",
                dict: "object"
            }
            
            json_type = python_to_json.get(param_type, "string")
            input_schema["properties"][param_name] = {"type": json_type}
            
            if param.default is inspect.Parameter.empty:
                input_schema["required"].append(param_name)
        
        # Build output schema from return type
        return_type = hints.get('return', Any)
        output_schema = {"type": "object"}  # Default to object
        
        self._tools[name] = {
            "function": func,
            "description": description or func.__doc__ or "",
            "input_schema": input_schema,
            "output_schema": output_schema
        }
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolInfo]:
        """List all registered tools."""
        return [
            ToolInfo(
                name=name,
                description=tool["description"],
                input_schema=tool["input_schema"],
                output_schema=tool["output_schema"]
            )
            for name, tool in self._tools.items()
        ]


class ResourceRegistry:
    """Registry for server resources."""
    
    def __init__(self):
        self._resources: Dict[str, Dict[str, Any]] = {}
    
    def register(self, uri: str, func: Callable, description: Optional[str] = None, mime_type: Optional[str] = None):
        """Register a resource function."""
        self._resources[uri] = {
            "function": func,
            "description": description or func.__doc__ or "",
            "mime_type": mime_type
        }
    
    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get a resource by URI."""
        return self._resources.get(uri)
    
    def list_resources(self) -> List[ResourceInfo]:
        """List all registered resources."""
        return [
            ResourceInfo(
                uri=uri,
                description=resource["description"],
                mime_type=resource["mime_type"]
            )
            for uri, resource in self._resources.items()
        ]


class PromptRegistry:
    """Registry for server prompts."""
    
    def __init__(self):
        self._prompts: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, func: Callable, description: Optional[str] = None):
        """Register a prompt function."""
        # Get parameter info for arguments
        sig = inspect.signature(func)
        arguments = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            arg_info = {
                "name": param_name,
                "description": f"Parameter {param_name}",
                "required": param.default is inspect.Parameter.empty
            }
            arguments.append(arg_info)
        
        self._prompts[name] = {
            "function": func,
            "description": description or func.__doc__ or "",
            "arguments": arguments
        }
    
    def get_prompt(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a prompt by name."""
        return self._prompts.get(name)
    
    def list_prompts(self) -> List[PromptInfo]:
        """List all registered prompts."""
        return [
            PromptInfo(
                name=name,
                description=prompt["description"],
                arguments=prompt["arguments"]
            )
            for name, prompt in self._prompts.items()
        ]


class Server:
    """
    Base class for MCP servers.
    
    Examples:
        >>> class MyServer(Server):
        ...     @tool("Add two numbers")
        ...     def add(self, a: int, b: int) -> int:
        ...         return a + b
        ...
        >>> server = MyServer(name="calculator")
        >>> run_server(server)
    """
    
    def __init__(self, name: str, config: Optional[ServerConfig] = None):
        self.name = name
        self.config = config or ServerConfig(name=name)
        
        self._tool_registry = ToolRegistry()
        self._resource_registry = ResourceRegistry()
        self._prompt_registry = PromptRegistry()
        
        self._mcp_server: Optional[MCPServer] = None
        self._running = False
        
        # Auto-register methods with decorators
        self._register_decorated_methods()
    
    def _register_decorated_methods(self):
        """Register methods that have been decorated."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_lmcp_tool'):
                tool_info = attr._lmcp_tool
                self._tool_registry.register(
                    tool_info['name'],
                    attr,
                    tool_info['description']
                )
            elif hasattr(attr, '_lmcp_resource'):
                resource_info = attr._lmcp_resource
                self._resource_registry.register(
                    resource_info['uri'],
                    attr,
                    resource_info['description'],
                    resource_info['mime_type']
                )
            elif hasattr(attr, '_lmcp_prompt'):
                prompt_info = attr._lmcp_prompt
                self._prompt_registry.register(
                    prompt_info['name'],
                    attr,
                    prompt_info['description']
                )
    
    async def start(self):
        """Start the MCP server."""
        if self._running:
            return
        
        logger.info(f"Starting MCP server: {self.name}")
        
        # Create MCP server instance
        self._mcp_server = MCPServer(self.config)
        
        # Register handlers
        await self._mcp_server.register_tool_handler(self._handle_tool_call)
        await self._mcp_server.register_resource_handler(self._handle_resource_request)
        await self._mcp_server.register_prompt_handler(self._handle_prompt_request)
        
        # Start the server
        await self._mcp_server.start()
        self._running = True
        
        logger.info(f"MCP server started: {self.name}")
    
    async def stop(self):
        """Stop the MCP server."""
        if not self._running:
            return
        
        logger.info(f"Stopping MCP server: {self.name}")
        
        if self._mcp_server:
            await self._mcp_server.stop()
            self._mcp_server = None
        
        self._running = False
        logger.info(f"MCP server stopped: {self.name}")
    
    async def _handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Handle tool call requests."""
        tool = self._tool_registry.get_tool(name)
        if not tool:
            return ToolResult(
                content=None,
                is_error=True,
                error_message=f"Tool '{name}' not found"
            )
        
        try:
            func = tool["function"]
            if inspect.iscoroutinefunction(func):
                result = await func(**arguments)
            else:
                result = func(**arguments)
            
            return ToolResult(content=result)
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return ToolResult(
                content=None,
                is_error=True,
                error_message=str(e)
            )
    
    async def _handle_resource_request(self, uri: str) -> ResourceResult:
        """Handle resource requests."""
        resource = self._resource_registry.get_resource(uri)
        if not resource:
            raise ValidationError(f"Resource '{uri}' not found")
        
        try:
            func = resource["function"]
            if inspect.iscoroutinefunction(func):
                result = await func()
            else:
                result = func()
            
            return ResourceResult(
                content=result,
                uri=uri,
                mime_type=resource["mime_type"]
            )
        except Exception as e:
            logger.error(f"Resource request failed: {e}")
            raise ValidationError(f"Failed to get resource '{uri}': {e}")
    
    async def _handle_prompt_request(self, name: str, arguments: Dict[str, Any]) -> PromptResult:
        """Handle prompt requests."""
        prompt = self._prompt_registry.get_prompt(name)
        if not prompt:
            raise ValidationError(f"Prompt '{name}' not found")
        
        try:
            func = prompt["function"]
            if inspect.iscoroutinefunction(func):
                result = await func(**arguments)
            else:
                result = func(**arguments)
            
            # Ensure result is a list of messages
            if isinstance(result, list):
                messages = result
            else:
                messages = [{"role": "user", "content": str(result)}]
            
            return PromptResult(messages=messages)
        except Exception as e:
            logger.error(f"Prompt request failed: {e}")
            raise ValidationError(f"Failed to get prompt '{name}': {e}")
    
    def list_tools(self) -> List[ToolInfo]:
        """List all available tools."""
        return self._tool_registry.list_tools()
    
    def list_resources(self) -> List[ResourceInfo]:
        """List all available resources."""
        return self._resource_registry.list_resources()
    
    def list_prompts(self) -> List[PromptInfo]:
        """List all available prompts."""
        return self._prompt_registry.list_prompts()


def tool(description: Optional[str] = None, name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to mark a method as an MCP tool.
    
    Args:
        description: Description of the tool
        name: Name of the tool (defaults to function name)
    
    Examples:
        >>> @tool("Add two numbers")
        ... def add(self, a: int, b: int) -> int:
        ...     return a + b
    """
    def decorator(func: F) -> F:
        tool_name = name or func.__name__
        func._lmcp_tool = {
            'name': tool_name,
            'description': description or func.__doc__ or ""
        }
        return func
    return decorator


def resource(uri: str, description: Optional[str] = None, mime_type: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to mark a method as an MCP resource.
    
    Args:
        uri: URI of the resource
        description: Description of the resource
        mime_type: MIME type of the resource
    
    Examples:
        >>> @resource("file://config.json", mime_type="application/json")
        ... def get_config(self) -> dict:
        ...     return {"setting": "value"}
    """
    def decorator(func: F) -> F:
        func._lmcp_resource = {
            'uri': uri,
            'description': description or func.__doc__ or "",
            'mime_type': mime_type
        }
        return func
    return decorator


def prompt(name: Optional[str] = None, description: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to mark a method as an MCP prompt.
    
    Args:
        name: Name of the prompt (defaults to function name)
        description: Description of the prompt
    
    Examples:
        >>> @prompt("greeting", "Generate a greeting message")
        ... def greeting(self, name: str) -> str:
        ...     return f"Hello, {name}!"
    """
    def decorator(func: F) -> F:
        prompt_name = name or func.__name__
        func._lmcp_prompt = {
            'name': prompt_name,
            'description': description or func.__doc__ or ""
        }
        return func
    return decorator


def server(name: str, config: Optional[ServerConfig] = None) -> Callable[[type], type]:
    """
    Class decorator to create an MCP server.
    
    Args:
        name: Name of the server
        config: Optional server configuration
    
    Examples:
        >>> @server("calculator")
        ... class Calculator:
        ...     @tool("Add two numbers")
        ...     def add(self, a: int, b: int) -> int:
        ...         return a + b
    """
    def decorator(cls: type) -> type:
        # Create a new class that inherits from Server
        class ServerClass(cls, Server):
            def __init__(self, *args, **kwargs):
                Server.__init__(self, name, config)
                cls.__init__(self, *args, **kwargs)
        
        ServerClass.__name__ = cls.__name__
        ServerClass.__qualname__ = cls.__qualname__
        return ServerClass
    
    return decorator


async def run_server(server_instance: Server, host: str = "localhost", port: int = 8080):
    """
    Run an MCP server instance.
    
    Args:
        server_instance: The server instance to run
        host: Host to bind to
        port: Port to bind to
    
    Examples:
        >>> server = MyServer(name="calculator")
        >>> await run_server(server)
    """
    try:
        await server_instance.start()
        
        # Keep the server running
        logger.info(f"Server running on {host}:{port}")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await server_instance.stop()
    except Exception as e:
        logger.error(f"Server error: {e}")
        await server_instance.stop()
        raise