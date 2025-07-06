"""
LMCP Client Implementation

Provides the main client interface for connecting to MCP servers.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .connection import ConnectionManager
from .exceptions import (
    ConnectionError,
    ResourceNotFoundError,
    ServerError,
    ToolNotFoundError,
)
from .protocol import MCPClient
from .types import (
    ConnectionConfig,
    HealthStatus,
    PromptInfo,
    PromptResult,
    ResourceInfo,
    ResourceResult,
    ServerInfo,
    ToolInfo,
    ToolResult,
)

logger = logging.getLogger(__name__)


class ToolProxy:
    """Proxy for accessing server tools."""

    def __init__(self, client: "Client"):
        self._client = client
        self._tools: Dict[str, ToolInfo] = {}

    def __getattr__(self, name: str) -> Any:
        """Get a tool by name."""
        if name.startswith("_"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        async def tool_call(*args, **kwargs):
            return await self._client.call_tool(name, *args, **kwargs)

        return tool_call

    async def list(self) -> List[ToolInfo]:
        """List all available tools."""
        return await self._client.list_tools()

    async def get_info(self, name: str) -> ToolInfo:
        """Get information about a specific tool."""
        tools = await self.list()
        for tool in tools:
            if tool.name == name:
                return tool
        raise ToolNotFoundError(f"Tool '{name}' not found")


class ResourceProxy:
    """Proxy for accessing server resources."""

    def __init__(self, client: "Client"):
        self._client = client
        self._resources: Dict[str, ResourceInfo] = {}

    async def get(self, uri: str) -> ResourceResult:
        """Get a resource by URI."""
        return await self._client.get_resource(uri)

    async def list(self) -> List[ResourceInfo]:
        """List all available resources."""
        return await self._client.list_resources()


class Client:
    """
    Main client class for connecting to MCP servers.

    Examples:
        >>> client = Client("filesystem://./docs")
        >>> await client.connect()
        >>> files = await client.tools.list_files(path=".")
        >>> await client.disconnect()

        >>> async with Client("git://./") as client:
        ...     status = await client.tools.get_status()
    """

    def __init__(
        self,
        uri: str,
        config: Optional[ConnectionConfig] = None,
        auto_connect: bool = True,
    ):
        self.uri = uri
        self.config = config or ConnectionConfig(uri=uri)
        self.auto_connect = auto_connect

        self._connection_manager = ConnectionManager(self.config)
        self._mcp_client: Optional[MCPClient] = None
        self._connected = False

        # Proxies
        self.tools = ToolProxy(self)
        self.resources = ResourceProxy(self)

        # Connection state
        self._server_info: Optional[ServerInfo] = None
        self._capabilities: Dict[str, Any] = {}

    async def connect(self) -> None:
        """Connect to the MCP server."""
        if self._connected:
            return

        try:
            logger.info(f"Connecting to MCP server at {self.uri}")

            # Create connection
            connection = await self._connection_manager.create_connection(self.uri)

            # Initialize MCP client
            self._mcp_client = MCPClient(connection)
            await self._mcp_client.initialize()

            # Get server info
            self._server_info = await self._mcp_client.get_server_info()
            self._capabilities = self._server_info.capabilities

            self._connected = True
            logger.info(f"Connected to MCP server: {self._server_info.name}")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise ConnectionError(f"Failed to connect to {self.uri}: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if not self._connected:
            return

        try:
            logger.info("Disconnecting from MCP server")

            if self._mcp_client:
                await self._mcp_client.close()
                self._mcp_client = None

            await self._connection_manager.close()
            self._connected = False

            logger.info("Disconnected from MCP server")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            raise ConnectionError(f"Failed to disconnect: {e}")

    async def __aenter__(self) -> "Client":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()

    @property
    def connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    @property
    def server_info(self) -> Optional[ServerInfo]:
        """Get server information."""
        return self._server_info

    async def health_check(self) -> HealthStatus:
        """Check the health of the connection."""
        if not self._connected or not self._mcp_client:
            return HealthStatus(
                status="unhealthy",
                last_check=datetime.now(),
                checks={"connection": "not connected"},
            )

        try:
            # Simple ping to check connection
            await self._mcp_client.ping()
            return HealthStatus(
                status="healthy",
                last_check=datetime.now(),
                checks={"connection": "ok", "ping": "ok"},
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                last_check=datetime.now(),
                checks={"connection": "error", "error": str(e)},
            )

    async def list_tools(self) -> List[ToolInfo]:
        """List all available tools."""
        if not self._connected or not self._mcp_client:
            raise ConnectionError("Not connected to server")

        try:
            return await self._mcp_client.list_tools()
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise ServerError(f"Failed to list tools: {e}")

    async def call_tool(self, tool_name: str, *args, **kwargs) -> ToolResult:
        """Call a tool on the server."""
        if not self._connected or not self._mcp_client:
            raise ConnectionError("Not connected to server")

        try:
            logger.debug(
                f"Calling tool '{tool_name}' with args={args}, kwargs={kwargs}"
            )
            result = await self._mcp_client.call_tool(tool_name, *args, **kwargs)
            return ToolResult(content=result)
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return ToolResult(content=None, is_error=True, error_message=str(e))

    async def list_resources(self) -> List[ResourceInfo]:
        """List all available resources."""
        if not self._connected or not self._mcp_client:
            raise ConnectionError("Not connected to server")

        try:
            return await self._mcp_client.list_resources()
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            raise ServerError(f"Failed to list resources: {e}")

    async def get_resource(self, uri: str) -> ResourceResult:
        """Get a resource by URI."""
        if not self._connected or not self._mcp_client:
            raise ConnectionError("Not connected to server")

        try:
            logger.debug(f"Getting resource: {uri}")
            result = await self._mcp_client.get_resource(uri)
            return ResourceResult(content=result, uri=uri)
        except Exception as e:
            logger.error(f"Failed to get resource: {e}")
            raise ResourceNotFoundError(f"Failed to get resource '{uri}': {e}")

    async def list_prompts(self) -> List[PromptInfo]:
        """List all available prompts."""
        if not self._connected or not self._mcp_client:
            raise ConnectionError("Not connected to server")

        try:
            return await self._mcp_client.list_prompts()
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            raise ServerError(f"Failed to list prompts: {e}")

    async def get_prompt(
        self, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> PromptResult:
        """Get a prompt by name."""
        if not self._connected or not self._mcp_client:
            raise ConnectionError("Not connected to server")

        try:
            logger.debug(f"Getting prompt '{name}' with arguments={arguments}")
            result = await self._mcp_client.get_prompt(name, arguments or {})
            return PromptResult(messages=result)
        except Exception as e:
            logger.error(f"Failed to get prompt: {e}")
            raise ServerError(f"Failed to get prompt '{name}': {e}")


def connect(uri: str, config: Optional[ConnectionConfig] = None) -> Client:
    """
    Create a new client connection to an MCP server.

    Args:
        uri: The URI of the MCP server to connect to
        config: Optional connection configuration

    Returns:
        A new Client instance

    Examples:
        >>> client = connect("filesystem://./docs")
        >>> async with client:
        ...     files = await client.tools.list_files(path=".")
    """
    return Client(uri, config)
