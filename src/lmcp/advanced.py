"""
LMCP Advanced Features

Easy-to-use advanced functionality like pipelines and batch operations.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import asynccontextmanager

from .client import Client, connect
from .middleware.base import MiddlewareChain
from .exceptions import LMCPError

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Advanced pipeline for managing multiple MCP servers with middleware.
    
    Makes it super easy to work with multiple servers and add cross-cutting concerns.
    
    Examples:
        >>> async with Pipeline() as pipeline:
        ...     pipeline.add_server("filesystem://./")
        ...     pipeline.add_middleware(LoggingMiddleware())
        ...     results = await pipeline.batch([
        ...         ("filesystem.list_files", {"path": "."}),
        ...         ("filesystem.read_file", {"path": "README.md"})
        ...     ])
    """
    
    def __init__(self):
        self._servers: Dict[str, Client] = {}
        self._middleware = MiddlewareChain()
        self._connected = False
    
    def add_server(self, uri: str, name: Optional[str] = None) -> None:
        """
        Add a server to the pipeline.
        
        Args:
            uri: Server URI to connect to
            name: Optional name for the server (defaults to parsed from URI)
        """
        if name is None:
            # Extract name from URI (e.g., "filesystem" from "stdio://filesystem-server")
            name = uri.split("://")[-1].split("-")[0].split("/")[0]
        
        self._servers[name] = connect(uri)
    
    def add_middleware(self, middleware) -> None:
        """Add middleware to the pipeline."""
        self._middleware.add_middleware(middleware)
    
    async def connect_all(self) -> None:
        """Connect to all servers."""
        if self._connected:
            return
        
        # Connect to all servers
        for name, client in self._servers.items():
            try:
                await client.connect()
                logger.info(f"Connected to server: {name}")
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")
                raise LMCPError(f"Failed to connect to server '{name}': {e}")
        
        # Initialize middleware
        await self._middleware.initialize_all()
        
        self._connected = True
    
    async def disconnect_all(self) -> None:
        """Disconnect from all servers."""
        if not self._connected:
            return
        
        # Shutdown middleware
        await self._middleware.shutdown_all()
        
        # Disconnect from all servers
        for name, client in self._servers.items():
            try:
                await client.disconnect()
                logger.info(f"Disconnected from server: {name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {name}: {e}")
        
        self._connected = False
    
    async def __aenter__(self) -> "Pipeline":
        """Async context manager entry."""
        await self.connect_all()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect_all()
    
    async def execute(self, server_name: str, operation: str, **kwargs) -> Any:
        """
        Execute a single operation on a server.
        
        Args:
            server_name: Name of the server
            operation: Operation to execute (e.g., "list_files")
            **kwargs: Arguments for the operation
            
        Returns:
            Operation result
        """
        if not self._connected:
            raise LMCPError("Pipeline not connected")
        
        if server_name not in self._servers:
            raise LMCPError(f"Server '{server_name}' not found in pipeline")
        
        client = self._servers[server_name]
        
        # Execute through tools proxy
        tool_func = getattr(client.tools, operation)
        return await tool_func(**kwargs)
    
    async def batch(self, operations: List[Tuple[str, Dict[str, Any]]]) -> List[Any]:
        """
        Execute multiple operations in parallel.
        
        Args:
            operations: List of (operation, kwargs) tuples
                       Format: [("server.tool", {"arg": "value"}), ...]
            
        Returns:
            List of results in the same order as operations
            
        Examples:
            >>> results = await pipeline.batch([
            ...     ("filesystem.list_files", {"path": "."}),
            ...     ("git.get_status", {}),
            ... ])
        """
        if not self._connected:
            raise LMCPError("Pipeline not connected")
        
        # Create tasks for all operations
        tasks = []
        for op_spec, kwargs in operations:
            if "." not in op_spec:
                raise LMCPError(f"Invalid operation format: {op_spec}. Use 'server.tool'")
            
            server_name, operation = op_spec.split(".", 1)
            task = asyncio.create_task(
                self.execute(server_name, operation, **kwargs)
            )
            tasks.append(task)
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "error": True,
                    "message": str(result),
                    "type": type(result).__name__
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_all_tools(self) -> Dict[str, List[Any]]:
        """Get tools from all connected servers."""
        if not self._connected:
            raise LMCPError("Pipeline not connected")
        
        all_tools = {}
        for name, client in self._servers.items():
            try:
                tools = await client.list_tools()
                all_tools[name] = tools
            except Exception as e:
                logger.error(f"Failed to get tools from {name}: {e}")
                all_tools[name] = []
        
        return all_tools
    
    async def get_all_resources(self) -> Dict[str, List[Any]]:
        """Get resources from all connected servers."""
        if not self._connected:
            raise LMCPError("Pipeline not connected")
        
        all_resources = {}
        for name, client in self._servers.items():
            try:
                resources = await client.list_resources()
                all_resources[name] = resources
            except Exception as e:
                logger.error(f"Failed to get resources from {name}: {e}")
                all_resources[name] = []
        
        return all_resources
    
    def get_server_names(self) -> List[str]:
        """Get names of all configured servers."""
        return list(self._servers.keys())
    
    def get_server(self, name: str) -> Optional[Client]:
        """Get a specific server client."""
        return self._servers.get(name)


# Convenience functions for common operations
async def quick_connect(*uris: str) -> Dict[str, Client]:
    """
    Quickly connect to multiple servers.
    
    Args:
        *uris: Server URIs to connect to
        
    Returns:
        Dictionary mapping server names to clients
        
    Examples:
        >>> servers = await quick_connect(
        ...     "filesystem://./",
        ...     "git://./",
        ...     "stdio://my-server"
        ... )
        >>> files = await servers["filesystem"].tools.list_files(path=".")
    """
    clients = {}
    
    for uri in uris:
        # Extract server name from URI
        name = uri.split("://")[-1].split("-")[0].split("/")[0]
        if name in clients:
            name = f"{name}_{len(clients)}"  # Handle duplicates
        
        client = connect(uri)
        await client.connect()
        clients[name] = client
    
    return clients


async def parallel_execute(*operations: Tuple[Client, str, Dict[str, Any]]) -> List[Any]:
    """
    Execute operations on multiple clients in parallel.
    
    Args:
        *operations: Tuples of (client, tool_name, kwargs)
        
    Returns:
        List of results
        
    Examples:
        >>> fs = connect("filesystem://./")
        >>> git = connect("git://./")
        >>> results = await parallel_execute(
        ...     (fs, "list_files", {"path": "."}),
        ...     (git, "get_status", {})
        ... )
    """
    tasks = []
    
    for client, tool_name, kwargs in operations:
        tool_func = getattr(client.tools, tool_name)
        task = asyncio.create_task(tool_func(**kwargs))
        tasks.append(task)
    
    return await asyncio.gather(*tasks, return_exceptions=True)


@asynccontextmanager
async def managed_servers(*uris: str):
    """
    Context manager for automatically managing multiple server connections.
    
    Args:
        *uris: Server URIs to connect to
        
    Yields:
        Dictionary of connected clients
        
    Examples:
        >>> async with managed_servers("filesystem://./", "git://./") as servers:
        ...     files = await servers["filesystem"].tools.list_files(path=".")
        ...     status = await servers["git"].tools.get_status()
    """
    clients = {}
    
    try:
        # Connect to all servers
        for uri in uris:
            name = uri.split("://")[-1].split("-")[0].split("/")[0]
            if name in clients:
                name = f"{name}_{len(clients)}"
            
            client = connect(uri)
            await client.connect()
            clients[name] = client
        
        yield clients
        
    finally:
        # Disconnect all clients
        for client in clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting client: {e}")


# Make commonly used imports available
__all__ = [
    "Pipeline",
    "quick_connect", 
    "parallel_execute",
    "managed_servers"
]