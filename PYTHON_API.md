# 🐍 LMCP Python API Guide

Use LMCP programmatically in your Python applications without the CLI.

## Quick Start

```python
import asyncio
from lmcp import SimpleMCP

# Create client
client = SimpleMCP()

# List available servers
client.list_servers()

# Install and test a server
client.install_server("hello-world")
await client.test_server("hello-world")

# Discover tools and parameters
schema = await client.inspect_server("hello-world")
print("Available tools:", schema)

# Use a tool
result = await client.call_tool("hello-world", "echo", message="Hello from Python!")
print(result)
```

## Installation

```bash
# Clone and install LMCP
git clone https://github.com/lhassa8/LMCP.git
cd LMCP

# Create virtual environment
python -m venv lmcp-env
source lmcp-env/bin/activate  # Windows: lmcp-env\Scripts\activate

# Install as package
pip install -e .
```

## Basic Usage

### 1. Import and Initialize

```python
from lmcp import SimpleMCP
import asyncio

# Create client instance
client = SimpleMCP()
```

### 2. Discover Servers

```python
# List all available servers
client.list_servers()

# Get server info
servers = client.servers
filesystem_server = servers["filesystem"]
print(f"Description: {filesystem_server.description}")
print(f"Verified: {filesystem_server.verified}")
```

### 3. Install Servers

```python
# Install a server (requires Node.js/npm)
success = client.install_server("filesystem")
if success:
    print("Server installed successfully!")
```

### 4. Test Servers

```python
async def test_server():
    # Test if server works
    is_working = await client.test_server("filesystem")
    if is_working:
        print("Server is ready to use!")
    return is_working

# Run async function
result = asyncio.run(test_server())
```

### 5. Discover Tools and Parameters

```python
async def discover_tools():
    # Inspect a server to see all available tools
    result = await client.inspect_server("filesystem")
    
    if "result" in result and "tools" in result["result"]:
        for tool in result["result"]["tools"]:
            print(f"Tool: {tool['name']}")
            print(f"Description: {tool.get('description', 'No description')}")
            
            # Show required parameters
            if 'inputSchema' in tool and 'properties' in tool['inputSchema']:
                required = tool['inputSchema'].get('required', [])
                print(f"Required parameters: {required}")
                
                for param, info in tool['inputSchema']['properties'].items():
                    print(f"  - {param} ({info.get('type', 'unknown')}): {info.get('description', 'No description')}")
            print()

# Run discovery
asyncio.run(discover_tools())
```

### 6. Use Tools

```python
async def use_filesystem():
    # First discover what parameters are needed
    schema = await client.get_tool_schema("filesystem", "list_directory")
    print("Tool schema:", schema)
    
    # List directory
    result = await client.call_tool(
        "filesystem", 
        "list_directory", 
        path="."
    )
    print("Directory contents:", result)
    
    # Read a file
    result = await client.call_tool(
        "filesystem",
        "read_file", 
        path="README.md"
    )
    print("File content:", result)

# Run async function
asyncio.run(use_filesystem())
```

## Complete Examples

### Example 1: File Operations

```python
import asyncio
from lmcp import SimpleMCP

async def file_operations():
    client = SimpleMCP()
    
    # Install and test filesystem server
    print("Installing filesystem server...")
    client.install_server("filesystem")
    
    print("Testing server...")
    if await client.test_server("filesystem"):
        print("✅ Server ready!")
    else:
        print("❌ Server not working")
        return
    
    # List current directory
    print("\n📁 Listing current directory:")
    result = await client.call_tool("filesystem", "list_directory", path=".")
    if "result" in result:
        for item in result["result"]["content"]:
            print(f"  - {item['name']} ({'dir' if item['type'] == 'directory' else 'file'})")
    
    # Create a test file
    print("\n📝 Creating test file:")
    await client.call_tool(
        "filesystem", 
        "write_file", 
        path="test_python_api.txt",
        content="Hello from LMCP Python API!"
    )
    
    # Read the file back
    print("\n📖 Reading test file:")
    result = await client.call_tool("filesystem", "read_file", path="test_python_api.txt")
    if "result" in result:
        print(f"Content: {result['result']['content']}")

# Run the example
if __name__ == "__main__":
    asyncio.run(file_operations())
```

### Example 2: Wikipedia Search

```python
import asyncio
from lmcp import SimpleMCP

async def wikipedia_search():
    client = SimpleMCP()
    
    # Install and test Wikipedia server
    client.install_server("wikipedia")
    
    if await client.test_server("wikipedia"):
        print("🔍 Searching Wikipedia for 'Python programming':")
        
        # Search for articles
        result = await client.call_tool(
            "wikipedia", 
            "findPage", 
            query="Python programming"
        )
        
        if "result" in result:
            pages = result["result"]["content"]
            print(f"Found {len(pages)} results:")
            for page in pages[:3]:  # Show first 3 results
                print(f"  - {page['title']}: {page['snippet'][:100]}...")
        
        # Get full page content
        print("\n📄 Getting page content:")
        result = await client.call_tool(
            "wikipedia",
            "getPage", 
            title="Python (programming language)"
        )
        
        if "result" in result:
            content = result["result"]["content"]
            print(f"Page content: {content[:200]}...")

# Run the example
if __name__ == "__main__":
    asyncio.run(wikipedia_search())
```

### Example 3: Hello World Testing

```python
import asyncio
from lmcp import SimpleMCP

async def hello_world_demo():
    client = SimpleMCP()
    
    # Install and test hello-world server
    client.install_server("hello-world")
    
    if await client.test_server("hello-world"):
        print("🎉 Running Hello World examples:")
        
        # Echo a message
        result = await client.call_tool(
            "hello-world", 
            "echo", 
            message="Hello from Python!"
        )
        print(f"Echo result: {result}")
        
        # Add two numbers
        result = await client.call_tool(
            "hello-world",
            "add",
            a=15,
            b=27
        )
        print(f"15 + 27 = {result}")
        
        # Get debug info
        result = await client.call_tool("hello-world", "debug")
        print(f"Debug info: {result}")

# Run the example
if __name__ == "__main__":
    asyncio.run(hello_world_demo())
```

### Example 4: Batch Server Testing

```python
import asyncio
from lmcp import SimpleMCP

async def test_all_verified_servers():
    client = SimpleMCP()
    
    # Get all verified servers
    verified_servers = [
        name for name, server in client.servers.items() 
        if server.verified
    ]
    
    print(f"Testing {len(verified_servers)} verified servers...")
    
    results = {}
    for server_name in verified_servers:
        print(f"\n🧪 Testing {server_name}...")
        
        # Install if needed
        client.install_server(server_name)
        
        # Test server
        is_working = await client.test_server(server_name)
        results[server_name] = is_working
        
        if is_working:
            print(f"✅ {server_name} is working!")
        else:
            print(f"❌ {server_name} failed")
    
    # Summary
    print(f"\n📊 Test Results:")
    working = sum(results.values())
    total = len(results)
    print(f"  Working: {working}/{total} servers")
    
    for server, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {server}")

# Run the example
if __name__ == "__main__":
    asyncio.run(test_all_verified_servers())
```

## Advanced Usage

### Custom Server Management

```python
from lmcp import SimpleMCP, Server

# Create client with custom server
client = SimpleMCP()

# Add a custom server
custom_server = Server(
    name="my-custom-server",
    description="My custom MCP server",
    install_cmd="npm install -g my-custom-mcp",
    run_cmd="npx my-custom-mcp",
    verified=False
)

client.servers["my-custom-server"] = custom_server
```

### Error Handling

```python
import asyncio
from lmcp import SimpleMCP

async def safe_tool_call():
    client = SimpleMCP()
    
    try:
        result = await client.call_tool("filesystem", "read_file", path="nonexistent.txt")
        
        if "error" in result:
            print(f"Tool error: {result['error']}")
        else:
            print(f"Success: {result}")
            
    except Exception as e:
        print(f"Python error: {e}")

asyncio.run(safe_tool_call())
```

### Async Context Manager Pattern

```python
import asyncio
from lmcp import SimpleMCP

class MCPSession:
    def __init__(self, server_name):
        self.client = SimpleMCP()
        self.server_name = server_name
        
    async def __aenter__(self):
        # Install and test server
        self.client.install_server(self.server_name)
        is_ready = await self.client.test_server(self.server_name)
        if not is_ready:
            raise RuntimeError(f"Server {self.server_name} not ready")
        return self.client
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass

# Usage
async def use_session():
    async with MCPSession("hello-world") as client:
        result = await client.call_tool("hello-world", "echo", message="Session demo!")
        print(result)

asyncio.run(use_session())
```

## Available Servers & Tools

### Verified Working Servers ✅

```python
# Filesystem operations (12 tools)
await client.call_tool("filesystem", "list_directory", path=".")
await client.call_tool("filesystem", "read_file", path="file.txt")
await client.call_tool("filesystem", "write_file", path="new.txt", content="data")

# Hello World testing (3 tools)  
await client.call_tool("hello-world", "echo", message="Hello!")
await client.call_tool("hello-world", "add", a=5, b=3)
await client.call_tool("hello-world", "debug")

# Wikipedia search (4 tools)
await client.call_tool("wikipedia", "findPage", query="python")
await client.call_tool("wikipedia", "getPage", title="Python")

# Sequential thinking (1 tool)
await client.call_tool("sequential-thinking", "sequentialthinking", thought="How to solve X")
```

## Tips & Best Practices

1. **Always use async/await** for tool calls
2. **Check for errors** in responses: `if "error" in result:`
3. **Install servers first** before testing or using
4. **Use virtual environments** to avoid conflicts
5. **Handle timeouts** for long-running operations

## Integration Examples

### Flask Web App

```python
from flask import Flask, jsonify
import asyncio
from lmcp import SimpleMCP

app = Flask(__name__)
client = SimpleMCP()

@app.route('/search/<query>')
def search_wikipedia(query):
    async def do_search():
        return await client.call_tool("wikipedia", "findPage", query=query)
    
    result = asyncio.run(do_search())
    return jsonify(result)

if __name__ == '__main__':
    # Install Wikipedia server on startup
    client.install_server("wikipedia")
    app.run()
```

### Jupyter Notebook

```python
# Cell 1: Setup
import asyncio
from lmcp import SimpleMCP

client = SimpleMCP()
client.install_server("filesystem")

# Cell 2: Test server
await client.test_server("filesystem")

# Cell 3: Use tools
result = await client.call_tool("filesystem", "list_directory", path=".")
print(result)
```

### Data Pipeline

```python
import asyncio
from lmcp import SimpleMCP

async def data_pipeline():
    client = SimpleMCP()
    
    # Setup servers
    for server in ["filesystem", "wikipedia"]:
        client.install_server(server)
        await client.test_server(server)
    
    # Read input data
    input_data = await client.call_tool("filesystem", "read_file", path="queries.txt")
    queries = input_data["result"]["content"].split("\n")
    
    # Process each query
    results = []
    for query in queries:
        if query.strip():
            result = await client.call_tool("wikipedia", "findPage", query=query.strip())
            results.append(result)
    
    # Save results
    output = "\n".join([str(r) for r in results])
    await client.call_tool("filesystem", "write_file", path="results.txt", content=output)
    
    print(f"Processed {len(results)} queries")

asyncio.run(data_pipeline())
```

---

**🚀 Start building with LMCP Python API today!**