"""
Integration tests for LMCP client-server communication.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from lmcp import Client, Server, tool, resource, prompt, run_server
from lmcp.types import ConnectionConfig, ServerConfig
from lmcp.exceptions import LMCPError, ConnectionError, ServerError


class TestServer(Server):
    """Test server for integration tests."""
    
    def __init__(self):
        super().__init__("test-integration-server")
        self.call_history = []
    
    @tool("Add two numbers together")
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        self.call_history.append(("add", {"a": a, "b": b}))
        return a + b
    
    @tool("Echo a message")
    def echo(self, message: str) -> str:
        """Echo the input message."""
        self.call_history.append(("echo", {"message": message}))
        return message
    
    @tool("Simulate an error")
    def error_tool(self, should_error: bool = True) -> str:
        """Tool that can simulate errors."""
        self.call_history.append(("error_tool", {"should_error": should_error}))
        if should_error:
            raise ValueError("Simulated error")
        return "success"
    
    @resource("test://data", description="Test data resource")
    def get_test_data(self) -> dict:
        """Get test data."""
        return {
            "message": "Hello from resource",
            "timestamp": "2024-01-01T00:00:00Z",
            "calls": len(self.call_history)
        }
    
    @resource("test://config", description="Server configuration")
    def get_config(self) -> dict:
        """Get server configuration."""
        return {
            "name": self.name,
            "version": "1.0.0",
            "features": ["tools", "resources", "prompts"]
        }
    
    @prompt("greeting", description="Generate a greeting")
    def greeting_prompt(self, name: str = "World") -> list:
        """Generate a greeting prompt."""
        return [
            {
                "role": "user",
                "content": f"Please greet {name}"
            }
        ]
    
    @prompt("help", description="Generate help information")
    def help_prompt(self, topic: str = "general") -> list:
        """Generate help prompt."""
        return [
            {
                "role": "assistant",
                "content": f"Help information for topic: {topic}"
            }
        ]


@pytest.mark.integration
class TestClientServerIntegration:
    """Integration tests for client-server communication."""
    
    @pytest.fixture
    async def test_server(self):
        """Create a test server instance."""
        server = TestServer()
        yield server
    
    @pytest.fixture
    async def mock_client_server_pair(self, test_server):
        """Create a mock client-server pair for testing."""
        # Mock the connection and protocol layers for testing
        with patch('lmcp.client.ConnectionManager'), \
             patch('lmcp.client.MCPClient') as mock_mcp_client:
            
            # Setup mock MCP client
            mock_mcp_instance = AsyncMock()
            mock_mcp_client.return_value = mock_mcp_instance
            
            # Mock server info
            mock_mcp_instance.get_server_info.return_value = test_server._server_info or {
                "name": test_server.name,
                "version": "1.0.0",
                "capabilities": {}
            }
            
            # Mock tool operations
            async def mock_list_tools():
                return test_server.list_tools()
            
            async def mock_call_tool(name, *args, **kwargs):
                # Simulate calling the actual server method
                result = await test_server._handle_tool_call(name, kwargs)
                if result.is_error:
                    raise Exception(result.error_message)
                return result.content
            
            async def mock_list_resources():
                return test_server.list_resources()
            
            async def mock_get_resource(uri):
                # Simulate calling the actual server method
                result = await test_server._handle_resource_request(uri)
                return result.content
            
            async def mock_list_prompts():
                return test_server.list_prompts()
            
            async def mock_get_prompt(name, arguments):
                # Simulate calling the actual server method
                result = await test_server._handle_prompt_request(name, arguments)
                return result.messages
            
            mock_mcp_instance.list_tools = mock_list_tools
            mock_mcp_instance.call_tool = mock_call_tool
            mock_mcp_instance.list_resources = mock_list_resources
            mock_mcp_instance.get_resource = mock_get_resource
            mock_mcp_instance.list_prompts = mock_list_prompts
            mock_mcp_instance.get_prompt = mock_get_prompt
            mock_mcp_instance.ping = AsyncMock()
            
            # Create client
            client = Client("stdio://test-server")
            
            yield client, test_server
    
    @pytest.mark.asyncio
    async def test_client_server_tool_communication(self, mock_client_server_pair):
        """Test client-server tool communication."""
        client, server = mock_client_server_pair
        
        async with client:
            # Test listing tools
            tools = await client.list_tools()
            assert len(tools) >= 3  # add, echo, error_tool
            
            tool_names = [tool.name for tool in tools]
            assert "add" in tool_names
            assert "echo" in tool_names
            assert "error_tool" in tool_names
            
            # Test calling tools
            result = await client.call_tool("add", a=5, b=3)
            assert result.content == 8
            assert not result.is_error
            
            # Test echo tool
            result = await client.call_tool("echo", message="Hello, World!")
            assert result.content == "Hello, World!"
            assert not result.is_error
            
            # Test error handling
            result = await client.call_tool("error_tool", should_error=True)
            assert result.is_error
            assert "Simulated error" in result.error_message
            
            # Test successful error_tool call
            result = await client.call_tool("error_tool", should_error=False)
            assert result.content == "success"
            assert not result.is_error
            
            # Check call history on server
            assert len(server.call_history) == 4
    
    @pytest.mark.asyncio
    async def test_client_server_resource_communication(self, mock_client_server_pair):
        """Test client-server resource communication."""
        client, server = mock_client_server_pair
        
        async with client:
            # Test listing resources
            resources = await client.list_resources()
            assert len(resources) >= 2  # test://data, test://config
            
            resource_uris = [res.uri for res in resources]
            assert "test://data" in resource_uris
            assert "test://config" in resource_uris
            
            # Test getting resources
            result = await client.get_resource("test://data")
            assert "message" in result.content
            assert result.content["message"] == "Hello from resource"
            assert result.uri == "test://data"
            
            result = await client.get_resource("test://config")
            assert result.content["name"] == server.name
            assert "features" in result.content
    
    @pytest.mark.asyncio
    async def test_client_server_prompt_communication(self, mock_client_server_pair):
        """Test client-server prompt communication."""
        client, server = mock_client_server_pair
        
        async with client:
            # Test listing prompts
            prompts = await client.list_prompts()
            assert len(prompts) >= 2  # greeting, help
            
            prompt_names = [prompt.name for prompt in prompts]
            assert "greeting" in prompt_names
            assert "help" in prompt_names
            
            # Test getting prompts
            result = await client.get_prompt("greeting", {"name": "Alice"})
            assert len(result.messages) == 1
            assert "Alice" in result.messages[0]["content"]
            
            result = await client.get_prompt("help", {"topic": "tools"})
            assert len(result.messages) == 1
            assert "tools" in result.messages[0]["content"]
    
    @pytest.mark.asyncio
    async def test_client_tool_proxy(self, mock_client_server_pair):
        """Test client tool proxy functionality."""
        client, server = mock_client_server_pair
        
        async with client:
            # Test using tool proxy
            result = await client.tools.add(a=10, b=20)
            assert result.content == 30
            
            # Test listing through proxy
            tools = await client.tools.list()
            assert len(tools) >= 3
            
            # Test getting tool info through proxy
            tool_info = await client.tools.get_info("add")
            assert tool_info.name == "add"
            assert "Add two numbers" in tool_info.description
    
    @pytest.mark.asyncio
    async def test_client_resource_proxy(self, mock_client_server_pair):
        """Test client resource proxy functionality."""
        client, server = mock_client_server_pair
        
        async with client:
            # Test using resource proxy
            result = await client.resources.get("test://data")
            assert "message" in result.content
            
            # Test listing through proxy
            resources = await client.resources.list()
            assert len(resources) >= 2
    
    @pytest.mark.asyncio
    async def test_client_health_check(self, mock_client_server_pair):
        """Test client health check functionality."""
        client, server = mock_client_server_pair
        
        async with client:
            health = await client.health_check()
            assert health.status == "healthy"
            assert "connection" in health.checks
            assert "ping" in health.checks
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test connection error handling."""
        # Test with invalid URI
        client = Client("invalid://nonexistent")
        
        with pytest.raises(ConnectionError):
            await client.connect()
    
    @pytest.mark.asyncio
    async def test_server_lifecycle(self, test_server):
        """Test server lifecycle management."""
        assert not test_server._running
        
        # Mock the MCP server for testing
        with patch('lmcp.server.MCPServer') as mock_mcp_server:
            mock_mcp_instance = AsyncMock()
            mock_mcp_server.return_value = mock_mcp_instance
            
            # Test start
            await test_server.start()
            assert test_server._running
            mock_mcp_instance.start.assert_called_once()
            
            # Test stop
            await test_server.stop()
            assert not test_server._running
            mock_mcp_instance.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mock_client_server_pair):
        """Test concurrent client operations."""
        client, server = mock_client_server_pair
        
        async with client:
            # Execute multiple operations concurrently
            tasks = [
                client.tools.add(a=i, b=i+1)
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verify all results
            for i, result in enumerate(results):
                expected = i + (i + 1)  # a + b
                assert result.content == expected
                assert not result.is_error
            
            # Check that all calls were recorded
            assert len(server.call_history) >= 5
    
    @pytest.mark.asyncio
    async def test_error_propagation(self, mock_client_server_pair):
        """Test error propagation from server to client."""
        client, server = mock_client_server_pair
        
        async with client:
            # Test server-side error
            result = await client.tools.error_tool(should_error=True)
            assert result.is_error
            assert "Simulated error" in result.error_message
            
            # Test non-existent tool
            with pytest.raises(Exception):  # Should raise an exception
                await client.tools.nonexistent_tool()
    
    @pytest.mark.asyncio 
    async def test_data_validation(self, mock_client_server_pair):
        """Test data validation in client-server communication."""
        client, server = mock_client_server_pair
        
        async with client:
            # Test with valid data
            result = await client.tools.add(a=5.5, b=2.3)
            assert abs(result.content - 7.8) < 0.001
            
            # Test with string that should be converted
            result = await client.tools.echo(message="test message")
            assert result.content == "test message"