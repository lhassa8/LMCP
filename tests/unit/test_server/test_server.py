"""
Unit tests for LMCP Server.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from lmcp.server import Server, ToolRegistry, ResourceRegistry, PromptRegistry, tool, resource, prompt
from lmcp.types import ServerConfig, ToolInfo, ResourceInfo, PromptInfo, ToolResult, ResourceResult, PromptResult
from lmcp.exceptions import ValidationError


class TestToolRegistry:
    """Test the ToolRegistry class."""
    
    def test_register_tool(self):
        """Test tool registration."""
        registry = ToolRegistry()
        
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        registry.register("add", add, "Add two numbers")
        
        tool = registry.get_tool("add")
        assert tool is not None
        assert tool["function"] == add
        assert tool["description"] == "Add two numbers"
        assert "a" in tool["input_schema"]["properties"]
        assert "b" in tool["input_schema"]["properties"]
    
    def test_register_tool_with_defaults(self):
        """Test tool registration with default parameters."""
        registry = ToolRegistry()
        
        def echo(message: str = "hello") -> str:
            return message
        
        registry.register("echo", echo)
        
        tool = registry.get_tool("echo")
        assert tool is not None
        assert "message" not in tool["input_schema"]["required"]
    
    def test_list_tools(self):
        """Test listing registered tools."""
        registry = ToolRegistry()
        
        def add(a: int, b: int) -> int:
            return a + b
        
        def subtract(a: int, b: int) -> int:
            return a - b
        
        registry.register("add", add)
        registry.register("subtract", subtract)
        
        tools = registry.list_tools()
        assert len(tools) == 2
        assert any(tool.name == "add" for tool in tools)
        assert any(tool.name == "subtract" for tool in tools)
    
    def test_get_nonexistent_tool(self):
        """Test getting a non-existent tool."""
        registry = ToolRegistry()
        
        tool = registry.get_tool("nonexistent")
        assert tool is None


class TestResourceRegistry:
    """Test the ResourceRegistry class."""
    
    def test_register_resource(self):
        """Test resource registration."""
        registry = ResourceRegistry()
        
        def get_data():
            return {"key": "value"}
        
        registry.register("data://test", get_data, "Test data", "application/json")
        
        resource = registry.get_resource("data://test")
        assert resource is not None
        assert resource["function"] == get_data
        assert resource["description"] == "Test data"
        assert resource["mime_type"] == "application/json"
    
    def test_list_resources(self):
        """Test listing registered resources."""
        registry = ResourceRegistry()
        
        def get_config():
            return {}
        
        def get_data():
            return {}
        
        registry.register("config://app", get_config)
        registry.register("data://users", get_data)
        
        resources = registry.list_resources()
        assert len(resources) == 2
        assert any(res.uri == "config://app" for res in resources)
        assert any(res.uri == "data://users" for res in resources)


class TestPromptRegistry:
    """Test the PromptRegistry class."""
    
    def test_register_prompt(self):
        """Test prompt registration."""
        registry = PromptRegistry()
        
        def greeting(name: str):
            return f"Hello, {name}!"
        
        registry.register("greeting", greeting, "Generate greeting")
        
        prompt = registry.get_prompt("greeting")
        assert prompt is not None
        assert prompt["function"] == greeting
        assert prompt["description"] == "Generate greeting"
        assert len(prompt["arguments"]) == 1
        assert prompt["arguments"][0]["name"] == "name"
    
    def test_list_prompts(self):
        """Test listing registered prompts."""
        registry = PromptRegistry()
        
        def help_prompt():
            return "Help text"
        
        def greeting_prompt(name: str):
            return f"Hello, {name}"
        
        registry.register("help", help_prompt)
        registry.register("greeting", greeting_prompt)
        
        prompts = registry.list_prompts()
        assert len(prompts) == 2
        assert any(p.name == "help" for p in prompts)
        assert any(p.name == "greeting" for p in prompts)


class TestServer:
    """Test the Server class."""
    
    def test_server_init(self, sample_server_config):
        """Test server initialization."""
        server = Server("test-server", sample_server_config)
        
        assert server.name == "test-server"
        assert server.config == sample_server_config
        assert not server._running
        assert isinstance(server._tool_registry, ToolRegistry)
        assert isinstance(server._resource_registry, ResourceRegistry)
        assert isinstance(server._prompt_registry, PromptRegistry)
    
    @pytest.mark.asyncio
    @patch('lmcp.server.MCPServer')
    async def test_server_start(self, mock_mcp_server, sample_server_config):
        """Test server start."""
        server = Server("test-server", sample_server_config)
        
        mock_mcp_instance = AsyncMock()
        mock_mcp_server.return_value = mock_mcp_instance
        
        await server.start()
        
        assert server._running
        mock_mcp_instance.register_tool_handler.assert_called_once()
        mock_mcp_instance.register_resource_handler.assert_called_once()
        mock_mcp_instance.register_prompt_handler.assert_called_once()
        mock_mcp_instance.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_server_stop(self):
        """Test server stop."""
        server = Server("test-server")
        server._running = True
        server._mcp_server = AsyncMock()
        
        await server.stop()
        
        assert not server._running
        server._mcp_server.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_success(self):
        """Test successful tool call handling."""
        server = Server("test-server")
        
        # Register a test tool
        def add(a: int, b: int) -> int:
            return a + b
        
        server._tool_registry.register("add", add)
        
        result = await server._handle_tool_call("add", {"a": 5, "b": 3})
        
        assert isinstance(result, ToolResult)
        assert result.content == 8
        assert not result.is_error
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_not_found(self):
        """Test tool call with non-existent tool."""
        server = Server("test-server")
        
        result = await server._handle_tool_call("nonexistent", {})
        
        assert isinstance(result, ToolResult)
        assert result.is_error
        assert "not found" in result.error_message
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_error(self):
        """Test tool call that raises an error."""
        server = Server("test-server")
        
        def error_tool():
            raise ValueError("Test error")
        
        server._tool_registry.register("error", error_tool)
        
        result = await server._handle_tool_call("error", {})
        
        assert isinstance(result, ToolResult)
        assert result.is_error
        assert "Test error" in result.error_message
    
    @pytest.mark.asyncio
    async def test_handle_resource_request_success(self):
        """Test successful resource request handling."""
        server = Server("test-server")
        
        def get_data():
            return {"key": "value"}
        
        server._resource_registry.register("data://test", get_data)
        
        result = await server._handle_resource_request("data://test")
        
        assert isinstance(result, ResourceResult)
        assert result.content == {"key": "value"}
        assert result.uri == "data://test"
    
    @pytest.mark.asyncio
    async def test_handle_resource_request_not_found(self):
        """Test resource request for non-existent resource."""
        server = Server("test-server")
        
        with pytest.raises(ValidationError, match="not found"):
            await server._handle_resource_request("data://nonexistent")
    
    @pytest.mark.asyncio
    async def test_handle_prompt_request_success(self):
        """Test successful prompt request handling."""
        server = Server("test-server")
        
        def greeting_prompt(name: str):
            return [{"role": "user", "content": f"Hello, {name}!"}]
        
        server._prompt_registry.register("greeting", greeting_prompt)
        
        result = await server._handle_prompt_request("greeting", {"name": "Alice"})
        
        assert isinstance(result, PromptResult)
        assert len(result.messages) == 1
        assert "Alice" in result.messages[0]["content"]
    
    @pytest.mark.asyncio
    async def test_handle_prompt_request_string_result(self):
        """Test prompt request that returns a string."""
        server = Server("test-server")
        
        def simple_prompt():
            return "Simple response"
        
        server._prompt_registry.register("simple", simple_prompt)
        
        result = await server._handle_prompt_request("simple", {})
        
        assert isinstance(result, PromptResult)
        assert len(result.messages) == 1
        assert result.messages[0]["content"] == "Simple response"


class MockDecoratedServer(Server):
    """Mock server with decorated methods for testing."""
    
    def __init__(self):
        super().__init__("mock-decorated")
    
    @tool("Add two numbers")
    def add(self, a: int, b: int) -> int:
        return a + b
    
    @resource("mock://data", "Mock data", "application/json")
    def get_data(self):
        return {"mock": "data"}
    
    @prompt("greeting", "Generate greeting")
    def greeting(self, name: str = "World"):
        return f"Hello, {name}!"


class TestServerDecorators:
    """Test server decorators."""
    
    def test_tool_decorator(self):
        """Test @tool decorator."""
        server = MockDecoratedServer()
        
        # Check that tool was registered
        tools = server.list_tools()
        assert len(tools) >= 1
        
        tool_names = [tool.name for tool in tools]
        assert "add" in tool_names
    
    def test_resource_decorator(self):
        """Test @resource decorator."""
        server = MockDecoratedServer()
        
        # Check that resource was registered
        resources = server.list_resources()
        assert len(resources) >= 1
        
        resource_uris = [res.uri for res in resources]
        assert "mock://data" in resource_uris
    
    def test_prompt_decorator(self):
        """Test @prompt decorator."""
        server = MockDecoratedServer()
        
        # Check that prompt was registered
        prompts = server.list_prompts()
        assert len(prompts) >= 1
        
        prompt_names = [prompt.name for prompt in prompts]
        assert "greeting" in prompt_names


class TestDecorators:
    """Test decorator functions."""
    
    def test_tool_decorator_function(self):
        """Test tool decorator function."""
        @tool("Test tool")
        def test_func():
            pass
        
        assert hasattr(test_func, '_lmcp_tool')
        assert test_func._lmcp_tool['name'] == 'test_func'
        assert test_func._lmcp_tool['description'] == 'Test tool'
    
    def test_tool_decorator_with_name(self):
        """Test tool decorator with custom name."""
        @tool("Test tool", name="custom_name")
        def test_func():
            pass
        
        assert test_func._lmcp_tool['name'] == 'custom_name'
    
    def test_resource_decorator_function(self):
        """Test resource decorator function."""
        @resource("test://uri", "Test resource", "text/plain")
        def test_func():
            pass
        
        assert hasattr(test_func, '_lmcp_resource')
        assert test_func._lmcp_resource['uri'] == 'test://uri'
        assert test_func._lmcp_resource['description'] == 'Test resource'
        assert test_func._lmcp_resource['mime_type'] == 'text/plain'
    
    def test_prompt_decorator_function(self):
        """Test prompt decorator function."""
        @prompt("test_prompt", "Test prompt")
        def test_func():
            pass
        
        assert hasattr(test_func, '_lmcp_prompt')
        assert test_func._lmcp_prompt['name'] == 'test_prompt'
        assert test_func._lmcp_prompt['description'] == 'Test prompt'