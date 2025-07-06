# LMCP Examples

This directory contains comprehensive examples demonstrating LMCP capabilities.

## 📁 Example Files

### Basic Examples
- **`basic_client.py`** - Simple client connecting to filesystem server
- **`basic_server.py`** - Calculator server with tools, resources, and prompts

### Advanced Examples  
- **`advanced_server.py`** - Database server with transactions and analytics
- **`middleware_example.py`** - Middleware usage for logging, caching, retries

### Configuration Examples
- **`config_example.json`** - Sample LMCP configuration file
- **`server_configs/`** - Various server configuration examples

## 🚀 Quick Start

### Running the Basic Client
```bash
python examples/basic_client.py
```

### Running the Calculator Server
```bash
python examples/basic_server.py
```

### Testing with CLI
```bash
# List tools on a server
lmcp client list-tools stdio://python examples/basic_server.py

# Call a tool
lmcp client call-tool stdio://python examples/basic_server.py add --args a=5 --args b=3

# Run a server
lmcp server run examples/basic_server.py:CalculatorServer
```

## 📚 Example Descriptions

### 1. Basic Client (`basic_client.py`)

Demonstrates:
- Connecting to MCP servers
- Listing tools and resources
- Calling tools with parameters
- Error handling

```python
import asyncio
from lmcp import connect

async def main():
    async with connect("stdio://mcp-server-filesystem") as client:
        tools = await client.list_tools()
        result = await client.tools.list_files(path=".")
```

### 2. Basic Server (`basic_server.py`)

Features:
- **Tools**: Math operations (add, subtract, multiply, divide, sqrt, power)
- **Resources**: Calculation history and statistics
- **Prompts**: Math problem generation and help
- **Validation**: Input validation and error handling

```python
from lmcp import Server, tool, resource, prompt

class CalculatorServer(Server):
    @tool("Add two numbers")
    def add(self, a: float, b: float) -> float:
        return a + b
    
    @resource("calculator://history")
    def get_history(self):
        return self.calculation_history
```

### 3. Advanced Server (`advanced_server.py`)

Advanced features:
- **Database Operations**: User and post management with SQLite
- **Transactions**: Begin, commit, rollback support
- **Analytics**: Post engagement and user statistics
- **Pagination**: Efficient data retrieval
- **Search**: Full-text search across posts
- **Validation**: Comprehensive input validation

```python
class DatabaseServer(Server):
    @tool("Create a new user")
    def create_user(self, username: str, email: str):
        # Validation and database operations
        
    @tool("Begin database transaction") 
    def begin_transaction(self, transaction_id: str):
        # Transaction management
```

### 4. Middleware Example (`middleware_example.py`)

Middleware capabilities:
- **Logging**: Request/response logging with timing
- **Caching**: Intelligent caching with TTL
- **Retries**: Automatic retry with exponential backoff
- **Metrics**: Performance monitoring and analytics
- **Pipelines**: Combine multiple middleware components

```python
from lmcp.middleware import LoggingMiddleware, CacheMiddleware
from lmcp.advanced import Pipeline

async with Pipeline() as pipeline:
    pipeline.add_middleware(LoggingMiddleware())
    pipeline.add_middleware(CacheMiddleware(ttl=300))
```

## 🔧 Configuration Examples

### Basic Connection Config
```python
from lmcp import ConnectionConfig

config = ConnectionConfig(
    uri="stdio://mcp-server-filesystem",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0
)
```

### Server Config
```python
from lmcp.types import ServerConfig

config = ServerConfig(
    name="my-server",
    description="Custom MCP server",
    transport="stdio",
    capabilities={"streaming": True}
)
```

## 🧪 Testing Examples

### Unit Testing
```python
import pytest
from lmcp import Client

@pytest.mark.asyncio
async def test_calculator():
    async with Client("stdio://python examples/basic_server.py") as client:
        result = await client.tools.add(a=2, b=3)
        assert result.content == 5
```

### Integration Testing
```python
async def test_database_operations():
    async with Client("stdio://python examples/advanced_server.py") as client:
        # Test user creation
        user = await client.tools.create_user(
            username="testuser", 
            email="test@example.com"
        )
        assert user.content["username"] == "testuser"
```

## 📊 Performance Examples

### Benchmarking
```python
import time
from lmcp import connect

async def benchmark_operations():
    async with connect("stdio://calculator-server") as client:
        start = time.time()
        
        # Perform 100 operations
        for i in range(100):
            await client.tools.add(a=i, b=i+1)
        
        duration = time.time() - start
        print(f"100 operations in {duration:.2f}s")
```

### Load Testing
```python
import asyncio
from lmcp import connect

async def load_test():
    tasks = []
    
    # Create 10 concurrent clients
    for i in range(10):
        task = asyncio.create_task(test_client(i))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
```

## 🔍 Debugging Examples

### Verbose Logging
```python
import logging
from lmcp import connect
from lmcp.middleware import LoggingMiddleware

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add verbose middleware
middleware = LoggingMiddleware({
    "level": "DEBUG",
    "log_requests": True,
    "log_responses": True,
    "log_timing": True
})
```

### Error Handling
```python
from lmcp.exceptions import LMCPError, ConnectionError, ServerError

try:
    async with connect("invalid://server") as client:
        result = await client.tools.nonexistent_tool()
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ServerError as e:
    print(f"Server error: {e}")
except LMCPError as e:
    print(f"LMCP error: {e}")
```

## 💡 Best Practices

### 1. Connection Management
- Always use async context managers (`async with`)
- Configure appropriate timeouts
- Handle connection errors gracefully

### 2. Server Design
- Use descriptive tool names and documentation
- Implement proper input validation
- Return structured, consistent responses

### 3. Error Handling
- Use specific exception types
- Provide helpful error messages
- Log errors appropriately

### 4. Performance
- Use connection pooling for multiple servers
- Implement caching for expensive operations
- Monitor performance with metrics middleware

### 5. Security
- Validate all inputs
- Use authentication middleware when needed
- Don't expose sensitive information in logs

## 🎯 Use Cases

### Development Tools
- Code analysis and formatting
- Build system integration
- Testing automation

### Data Processing
- ETL operations
- Database management
- Analytics and reporting

### System Integration
- API orchestration
- Service composition
- Workflow automation

### AI/ML Applications
- Model serving
- Data preprocessing
- Result post-processing

## 📖 Additional Resources

- [LMCP Documentation](../docs/)
- [API Reference](../docs/api.md)
- [Configuration Guide](../docs/configuration.md)
- [Deployment Guide](../docs/deployment.md)

## 🤝 Contributing

Want to add more examples? Please:

1. Follow the existing code style
2. Include comprehensive documentation
3. Add error handling
4. Test your examples
5. Update this README

## 📝 License

These examples are provided under the same MIT license as LMCP.