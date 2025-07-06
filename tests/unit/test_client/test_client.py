"""
Unit tests for LMCP Client.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from lmcp.client import Client, ToolProxy, ResourceProxy, connect
from lmcp.types import ConnectionConfig, ServerInfo, ToolInfo, ResourceInfo
from lmcp.exceptions import ConnectionError, ServerError


class TestClient:
    """Test the Client class."""
    
    @pytest.mark.asyncio
    async def test_client_init(self, sample_connection_config):
        """Test client initialization."""
        client = Client("stdio://test", sample_connection_config)
        
        assert client.uri == "stdio://test"
        assert client.config == sample_connection_config
        assert not client.connected
        assert client.server_info is None
        assert isinstance(client.tools, ToolProxy)
        assert isinstance(client.resources, ResourceProxy)
    
    @pytest.mark.asyncio
    @patch('lmcp.client.ConnectionManager')
    @patch('lmcp.client.MCPClient')
    async def test_client_connect_success(self, mock_mcp_client, mock_connection_manager):
        """Test successful client connection."""
        # Setup mocks
        mock_connection = AsyncMock()
        mock_connection_manager.return_value.create_connection.return_value = mock_connection
        
        mock_mcp_instance = AsyncMock()
        mock_mcp_client.return_value = mock_mcp_instance
        mock_mcp_instance.get_server_info.return_value = ServerInfo(
            name="test-server",
            version="1.0.0",
            capabilities={}
        )
        
        client = Client("stdio://test")
        
        # Test connection
        await client.connect()
        
        assert client.connected
        assert client.server_info.name == "test-server"
        mock_connection_manager.return_value.create_connection.assert_called_once()
        mock_mcp_instance.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('lmcp.client.ConnectionManager')
    async def test_client_connect_failure(self, mock_connection_manager):
        """Test client connection failure."""
        # Setup mock to fail
        mock_connection_manager.return_value.create_connection.side_effect = Exception("Connection failed")
        
        client = Client("stdio://test")
        
        # Test connection failure
        with pytest.raises(ConnectionError, match="Failed to connect"):
            await client.connect()
        
        assert not client.connected
        assert client.server_info is None
    
    @pytest.mark.asyncio
    async def test_client_disconnect(self):
        """Test client disconnection."""
        client = Client("stdio://test")
        
        # Mock connected state
        client._connected = True
        client._mcp_client = AsyncMock()
        client._connection_manager = AsyncMock()
        
        await client.disconnect()
        
        assert not client.connected
        client._mcp_client.close.assert_called_once()
        client._connection_manager.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client as async context manager."""
        with patch.object(Client, 'connect') as mock_connect, \
             patch.object(Client, 'disconnect') as mock_disconnect:
            
            async with Client("stdio://test") as client:
                assert isinstance(client, Client)
            
            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_client_health_check_connected(self):
        """Test health check when connected."""
        client = Client("stdio://test")
        client._connected = True
        client._mcp_client = AsyncMock()
        
        health = await client.health_check()
        
        assert health.status == "healthy"
        client._mcp_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_client_health_check_disconnected(self):
        """Test health check when disconnected."""
        client = Client("stdio://test")
        
        health = await client.health_check()
        
        assert health.status == "unhealthy"
        assert health.checks["connection"] == "not connected"
    
    @pytest.mark.asyncio
    async def test_list_tools_success(self):
        """Test successful tool listing."""
        client = Client("stdio://test")
        client._connected = True
        client._mcp_client = AsyncMock()
        
        mock_tools = [
            ToolInfo(name="add", description="Add numbers"),
            ToolInfo(name="subtract", description="Subtract numbers")
        ]
        client._mcp_client.list_tools.return_value = mock_tools
        
        tools = await client.list_tools()
        
        assert len(tools) == 2
        assert tools[0].name == "add"
        assert tools[1].name == "subtract"
    
    @pytest.mark.asyncio
    async def test_list_tools_not_connected(self):
        """Test tool listing when not connected."""
        client = Client("stdio://test")
        
        with pytest.raises(ConnectionError, match="Not connected"):
            await client.list_tools()
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successful tool call."""
        client = Client("stdio://test")
        client._connected = True
        client._mcp_client = AsyncMock()
        client._mcp_client.call_tool.return_value = 8
        
        result = await client.call_tool("add", a=5, b=3)
        
        assert result.content == 8
        assert not result.is_error
        client._mcp_client.call_tool.assert_called_once_with("add", a=5, b=3)
    
    @pytest.mark.asyncio
    async def test_call_tool_error(self):
        """Test tool call with error."""
        client = Client("stdio://test")
        client._connected = True
        client._mcp_client = AsyncMock()
        client._mcp_client.call_tool.side_effect = Exception("Tool error")
        
        result = await client.call_tool("add", a=5, b=3)
        
        assert result.is_error
        assert "Tool error" in result.error_message
    
    @pytest.mark.asyncio
    async def test_list_resources_success(self):
        """Test successful resource listing."""
        client = Client("stdio://test")
        client._connected = True
        client._mcp_client = AsyncMock()
        
        mock_resources = [
            ResourceInfo(uri="file://test.txt", description="Test file"),
            ResourceInfo(uri="db://data", description="Database data")
        ]
        client._mcp_client.list_resources.return_value = mock_resources
        
        resources = await client.list_resources()
        
        assert len(resources) == 2
        assert resources[0].uri == "file://test.txt"
        assert resources[1].uri == "db://data"
    
    @pytest.mark.asyncio
    async def test_get_resource_success(self):
        """Test successful resource retrieval."""
        client = Client("stdio://test")
        client._connected = True
        client._mcp_client = AsyncMock()
        client._mcp_client.get_resource.return_value = "resource content"
        
        result = await client.get_resource("file://test.txt")
        
        assert result.content == "resource content"
        assert result.uri == "file://test.txt"


class TestToolProxy:
    """Test the ToolProxy class."""
    
    @pytest.mark.asyncio
    async def test_tool_proxy_getattr(self):
        """Test tool proxy dynamic attribute access."""
        client = AsyncMock()
        proxy = ToolProxy(client)
        
        # Test accessing a tool
        tool_func = proxy.add
        assert callable(tool_func)
    
    @pytest.mark.asyncio
    async def test_tool_proxy_call(self):
        """Test tool proxy calling tools."""
        client = AsyncMock()
        proxy = ToolProxy(client)
        
        # Mock the client's call_tool method
        client.call_tool.return_value = "result"
        
        # Call through proxy
        result = await proxy.add(5, 3)
        
        client.call_tool.assert_called_once_with("add", 5, 3)
    
    @pytest.mark.asyncio
    async def test_tool_proxy_list(self):
        """Test tool proxy list method."""
        client = AsyncMock()
        proxy = ToolProxy(client)
        
        mock_tools = [ToolInfo(name="add", description="Add numbers")]
        client.list_tools.return_value = mock_tools
        
        tools = await proxy.list()
        
        assert tools == mock_tools
        client.list_tools.assert_called_once()
    
    def test_tool_proxy_private_attr(self):
        """Test that private attributes raise AttributeError."""
        client = AsyncMock()
        proxy = ToolProxy(client)
        
        with pytest.raises(AttributeError):
            _ = proxy._private_attr


class TestResourceProxy:
    """Test the ResourceProxy class."""
    
    @pytest.mark.asyncio
    async def test_resource_proxy_get(self):
        """Test resource proxy get method."""
        client = AsyncMock()
        proxy = ResourceProxy(client)
        
        result = await proxy.get("file://test.txt")
        
        client.get_resource.assert_called_once_with("file://test.txt")
    
    @pytest.mark.asyncio
    async def test_resource_proxy_list(self):
        """Test resource proxy list method."""
        client = AsyncMock()
        proxy = ResourceProxy(client)
        
        mock_resources = [ResourceInfo(uri="file://test.txt")]
        client.list_resources.return_value = mock_resources
        
        resources = await proxy.list()
        
        assert resources == mock_resources
        client.list_resources.assert_called_once()


class TestConnectFunction:
    """Test the connect function."""
    
    def test_connect_creates_client(self):
        """Test that connect creates a Client instance."""
        client = connect("stdio://test")
        
        assert isinstance(client, Client)
        assert client.uri == "stdio://test"
    
    def test_connect_with_config(self, sample_connection_config):
        """Test connect with custom config."""
        client = connect("stdio://test", sample_connection_config)
        
        assert client.config == sample_connection_config