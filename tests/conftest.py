"""
Pytest configuration and fixtures for LMCP tests.
"""

import pytest
import asyncio
import tempfile
import sqlite3
from pathlib import Path
from typing import AsyncGenerator, Generator

from lmcp import Server, Client, tool, resource, prompt
from lmcp.types import ConnectionConfig, ServerConfig
from lmcp.exceptions import LMCPError


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_connection_config() -> ConnectionConfig:
    """Sample connection configuration."""
    return ConnectionConfig(
        uri="stdio://test-server",
        timeout=10.0,
        max_retries=2,
        retry_delay=0.1
    )


@pytest.fixture
def sample_server_config() -> ServerConfig:
    """Sample server configuration."""
    return ServerConfig(
        name="test-server",
        version="1.0.0",
        description="Test MCP server",
        transport="stdio"
    )


class MockServer(Server):
    """Mock server for testing."""
    
    def __init__(self):
        super().__init__(name="mock-server")
        self.call_count = 0
        self.last_args = None
        self.last_kwargs = None
    
    @tool("Add two numbers")
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        self.call_count += 1
        self.last_args = (a, b)
        return a + b
    
    @tool("Echo input")
    def echo(self, message: str) -> str:
        """Echo the input message."""
        self.call_count += 1
        self.last_kwargs = {"message": message}
        return message
    
    @tool("Raise error")
    def error_tool(self, should_error: bool = True) -> str:
        """Tool that optionally raises an error."""
        self.call_count += 1
        if should_error:
            raise ValueError("Test error")
        return "success"
    
    @resource("mock://data", description="Mock data resource")
    def get_data(self) -> dict:
        """Get mock data."""
        return {
            "data": "mock_value",
            "timestamp": "2024-01-01T00:00:00Z",
            "calls": self.call_count
        }
    
    @resource("mock://config", description="Mock config resource")
    def get_config(self) -> dict:
        """Get mock configuration."""
        return {
            "server": "mock-server",
            "version": "1.0.0",
            "features": ["tools", "resources", "prompts"]
        }
    
    @prompt("greeting", description="Generate greeting prompt")
    def greeting_prompt(self, name: str = "World") -> list:
        """Generate a greeting prompt."""
        return [
            {
                "role": "user",
                "content": f"Generate a greeting for {name}"
            }
        ]
    
    @prompt("help", description="Generate help prompt")
    def help_prompt(self, topic: str = "general") -> list:
        """Generate a help prompt."""
        return [
            {
                "role": "assistant",
                "content": f"Here is help information about {topic}."
            }
        ]


@pytest.fixture
async def mock_server() -> AsyncGenerator[MockServer, None]:
    """Create a mock server instance."""
    server = MockServer()
    yield server


@pytest.fixture
def sample_database(temp_dir: Path) -> Path:
    """Create a sample SQLite database for testing."""
    db_path = temp_dir / "test.db"
    
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            INSERT INTO users (id, username, email) VALUES
                (1, 'alice', 'alice@example.com'),
                (2, 'bob', 'bob@example.com');
            
            INSERT INTO posts (id, user_id, title, content) VALUES
                (1, 1, 'First Post', 'Hello World!'),
                (2, 1, 'Second Post', 'More content here'),
                (3, 2, 'Bob Post', 'Bob says hello');
        """)
    
    return db_path


@pytest.fixture
def sample_request_data() -> dict:
    """Sample MCP request data."""
    return {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "add",
            "arguments": {"a": 5, "b": 3}
        },
        "id": "test-request-1"
    }


@pytest.fixture
def sample_response_data() -> dict:
    """Sample MCP response data."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": "8"
                }
            ]
        },
        "id": "test-request-1"
    }


@pytest.fixture
def sample_error_response() -> dict:
    """Sample MCP error response."""
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32000,
            "message": "Tool execution failed",
            "data": {"tool": "add", "error": "Invalid arguments"}
        },
        "id": "test-request-1"
    }


@pytest.fixture
def sample_notification() -> dict:
    """Sample MCP notification."""
    return {
        "jsonrpc": "2.0",
        "method": "notifications/progress",
        "params": {
            "progressToken": "progress-1",
            "progress": 50,
            "total": 100
        }
    }


class MockTransport:
    """Mock transport for testing."""
    
    def __init__(self):
        self.sent_messages = []
        self.received_messages = []
        self.connected = False
        self.should_fail = False
        self.delay = 0.0
    
    async def connect(self, uri: str) -> None:
        """Mock connect."""
        if self.should_fail:
            raise LMCPError("Mock connection failure")
        self.connected = True
    
    async def disconnect(self) -> None:
        """Mock disconnect."""
        self.connected = False
    
    async def send(self, data: dict) -> None:
        """Mock send."""
        if not self.connected:
            raise LMCPError("Not connected")
        if self.should_fail:
            raise LMCPError("Mock send failure")
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        self.sent_messages.append(data)
    
    async def receive(self) -> dict:
        """Mock receive."""
        if not self.connected:
            raise LMCPError("Not connected")
        if self.should_fail:
            raise LMCPError("Mock receive failure")
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        if self.received_messages:
            return self.received_messages.pop(0)
        
        # Return a default response
        return {
            "jsonrpc": "2.0",
            "result": {"mock": "response"},
            "id": "mock-id"
        }
    
    async def ping(self) -> None:
        """Mock ping."""
        if not self.connected:
            raise LMCPError("Not connected")
        if self.should_fail:
            raise LMCPError("Mock ping failure")
    
    def add_received_message(self, message: dict) -> None:
        """Add a message to the receive queue."""
        self.received_messages.append(message)


@pytest.fixture
def mock_transport() -> MockTransport:
    """Create a mock transport instance."""
    return MockTransport()


# Async test helpers
@pytest.fixture
async def connected_mock_transport(mock_transport: MockTransport) -> MockTransport:
    """Create a connected mock transport."""
    await mock_transport.connect("mock://test")
    return mock_transport


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow