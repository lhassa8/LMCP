# 🚀 LMCP Client Guide - Using Other People's MCP Servers

LMCP makes it incredibly easy to use existing MCP servers in your Python projects. This guide shows you exactly how to connect to and use any MCP server with just a few lines of code.

## ⚡ Quick Start - Connect to Any MCP Server

```python
import asyncio
from lmcp import connect

async def main():
    # Connect to ANY MCP server with one line!
    async with connect("stdio://npx @modelcontextprotocol/server-filesystem ./") as fs:
        
        # Tools become Python methods automatically
        files = await fs.tools.read_directory(path=".")
        content = await fs.tools.read_file(path="README.md")
        
        print(f"Found {len(files.content)} files")
        print(f"README preview: {content.content[:100]}...")

asyncio.run(main())
```

**That's it!** Any MCP server becomes as easy to use as a Python library.

## 🌟 Why LMCP for Clients?

- **🔗 One-Line Connections**: `async with connect("server://") as client:`
- **🎯 Natural Tool Calls**: `await client.tools.my_tool(param="value")`
- **🔍 Auto-Discovery**: Tools and resources are discovered automatically
- **🛡️ Smart Error Handling**: Comprehensive error types and messages
- **⚡ High Performance**: Connection pooling, batching, parallel operations
- **🧩 Multi-Server**: Easily coordinate between multiple servers

## 📡 Connecting to Popular MCP Servers

### 1. Filesystem Server
```python
# Read and write files safely
async with connect("stdio://npx @modelcontextprotocol/server-filesystem ./") as fs:
    files = await fs.tools.read_directory(path=".")
    content = await fs.tools.read_file(path="config.json")
    await fs.tools.write_file(path="output.txt", content="Hello!")
```

### 2. Git Server
```python
# Git operations made easy
async with connect("stdio://npx @modelcontextprotocol/server-git") as git:
    status = await git.tools.git_status()
    log = await git.tools.git_log(limit=10)
    diff = await git.tools.git_diff()
```

### 3. Database Servers
```python
# Database operations
async with connect("stdio://python database_server.py") as db:
    user = await db.tools.create_user(name="John", email="john@example.com")
    posts = await db.tools.get_posts(user_id=user.content["id"])
```

### 4. API Servers
```python
# REST API integration
async with connect("stdio://node api_server.js") as api:
    response = await api.tools.get_weather(city="New York")
    data = await api.tools.fetch_data(endpoint="/users", params={"limit": 10})
```

### 5. AI/ML Servers
```python
# Machine learning models
async with connect("stdio://python ml_server.py") as ml:
    prediction = await ml.tools.predict(features=[1.2, 3.4, 5.6])
    embedding = await ml.tools.embed(text="Hello world")
```

## 🔍 Discovery and Exploration

### Discover Available Tools
```python
async with connect("stdio://any-server") as client:
    # See what's available
    tools = await client.list_tools()
    resources = await client.list_resources()
    
    print("🛠️ Available tools:")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")
        
    print("📁 Available resources:")
    for resource in resources:
        print(f"  • {resource.uri}: {resource.description}")
```

### Inspect Tool Details
```python
async with connect("stdio://server") as client:
    tools = await client.list_tools()
    
    for tool in tools:
        print(f"\n🔧 {tool.name}")
        print(f"   Description: {tool.description}")
        if hasattr(tool, 'inputSchema'):
            print(f"   Parameters: {tool.inputSchema}")
```

## 🛠️ Advanced Client Patterns

### 1. Error Handling
```python
from lmcp.exceptions import ConnectionError, ToolNotFoundError, ServerError

try:
    async with connect("stdio://server") as client:
        result = await client.tools.my_tool(param="value")
        
except ConnectionError:
    print("❌ Could not connect to server")
except ToolNotFoundError:
    print("❌ Tool not available")
except ServerError as e:
    print(f"❌ Server error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

### 2. Configuration and Timeouts
```python
from lmcp import connect, ConnectionConfig

config = ConnectionConfig(
    timeout=30.0,           # Connection timeout
    max_retries=3,          # Retry failed connections
    retry_delay=1.0         # Delay between retries
)

async with connect("stdio://slow-server", config=config) as client:
    result = await client.tools.heavy_computation()
```

### 3. Batch Operations
```python
async with connect("stdio://server") as client:
    # Execute multiple operations in parallel
    results = await asyncio.gather(
        client.tools.operation1(x=1),
        client.tools.operation2(y=2), 
        client.tools.operation3(z=3)
    )
    
    for i, result in enumerate(results):
        print(f"Operation {i+1}: {result.content}")
```

### 4. Resource Access
```python
async with connect("stdio://server") as client:
    # List available resources
    resources = await client.list_resources()
    
    # Get specific resources
    config = await client.resources.get("config://settings")
    data = await client.resources.get("data://latest")
    
    print(f"Config: {config.content}")
    print(f"Data: {data.content}")
```

### 5. Multi-Server Coordination
```python
# Use multiple servers together
async with connect("stdio://git-server") as git, \
           connect("stdio://filesystem-server") as fs:
    
    # Get git status
    status = await git.tools.git_status()
    
    # Read files
    files = await fs.tools.read_directory(path=".")
    
    # Combine information
    report = {
        "git_status": status.content,
        "file_count": len(files.content)
    }
```

## 🎯 Real-World Examples

### Example 1: Code Analysis Pipeline
```python
async def analyze_codebase():
    """Analyze a codebase using multiple MCP servers."""
    
    # Connect to analysis servers
    async with connect("stdio://git-server") as git, \
               connect("stdio://filesystem-server") as fs, \
               connect("stdio://python linter-server.py") as linter:
        
        # Get git info
        commits = await git.tools.git_log(limit=10)
        
        # Read source files
        python_files = await fs.tools.find_files(pattern="*.py")
        
        # Run analysis on each file
        analysis_results = []
        for file_path in python_files.content:
            content = await fs.tools.read_file(path=file_path)
            analysis = await linter.tools.analyze_code(
                code=content.content,
                file_path=file_path
            )
            analysis_results.append(analysis.content)
        
        return {
            "recent_commits": commits.content,
            "analysis": analysis_results
        }
```

### Example 2: Data Processing Workflow
```python
async def process_data_pipeline():
    """Process data using multiple specialized servers."""
    
    async with connect("stdio://database-server") as db, \
               connect("stdio://python ml-server.py") as ml, \
               connect("stdio://node api-server.js") as api:
        
        # Extract data
        raw_data = await db.tools.query(
            sql="SELECT * FROM raw_data WHERE processed = false"
        )
        
        # Transform with ML
        processed_data = []
        for row in raw_data.content:
            prediction = await ml.tools.predict(features=row["features"])
            row["prediction"] = prediction.content
            processed_data.append(row)
        
        # Load to external API
        for row in processed_data:
            await api.tools.post_data(endpoint="/results", data=row)
            await db.tools.mark_processed(id=row["id"])
        
        return len(processed_data)
```

### Example 3: DevOps Automation
```python
async def deploy_application():
    """Automate deployment using MCP servers."""
    
    async with connect("stdio://git-server") as git, \
               connect("stdio://docker-server") as docker, \
               connect("stdio://kubernetes-server") as k8s:
        
        # Check git status
        status = await git.tools.git_status()
        if status.content["dirty"]:
            raise Exception("Repository has uncommitted changes")
        
        # Build Docker image
        build_result = await docker.tools.build_image(
            dockerfile="Dockerfile",
            tag=f"myapp:{status.content['commit_hash'][:8]}"
        )
        
        # Deploy to Kubernetes
        deployment = await k8s.tools.deploy(
            image=build_result.content["image_name"],
            replicas=3
        )
        
        return deployment.content
```

## 🔧 CLI for Quick Testing

LMCP includes a powerful CLI for testing servers:

```bash
# Discover tools on any server
lmcp client list-tools "stdio://server-command"

# Call tools directly from command line
lmcp client call-tool "stdio://server" tool_name --args param=value

# Get resources
lmcp client list-resources "stdio://server"

# Check server health
lmcp client health "stdio://server"
```

## 📚 Integration Patterns

### Django/Flask Integration
```python
# In your web application
from lmcp import connect

async def api_endpoint(request):
    async with connect("stdio://data-server") as server:
        result = await server.tools.process_request(
            data=request.json
        )
        return JsonResponse(result.content)
```

### Jupyter Notebook Integration  
```python
# In a notebook cell
import asyncio
from lmcp import connect

# Connect to analysis server
client = await connect("stdio://analysis-server").__aenter__()

# Use throughout notebook
data = await client.tools.load_dataset(name="sales_data")
analysis = await client.tools.analyze(data=data.content)

# Remember to cleanup
await client.__aexit__(None, None, None)
```

### Background Task Integration
```python
# With Celery or similar
from celery import Celery
from lmcp import connect

app = Celery('myapp')

@app.task
async def process_with_mcp(data):
    async with connect("stdio://processor-server") as processor:
        result = await processor.tools.process(data=data)
        return result.content
```

## 🛡️ Best Practices

### 1. Connection Management
- ✅ Always use `async with connect()` for automatic cleanup
- ✅ Configure appropriate timeouts for your use case  
- ✅ Handle connection errors gracefully
- ✅ Consider connection pooling for high-traffic applications

### 2. Error Handling
- ✅ Use specific exception types (`ConnectionError`, `ToolNotFoundError`, etc.)
- ✅ Provide fallback behavior for unavailable servers
- ✅ Log errors appropriately for debugging
- ✅ Validate tool results before using them

### 3. Performance
- ✅ Reuse connections for multiple operations
- ✅ Use `asyncio.gather()` for parallel operations
- ✅ Implement caching for expensive operations
- ✅ Monitor performance with timing

### 4. Security
- ✅ Validate all inputs before sending to servers
- ✅ Don't log sensitive data
- ✅ Use authentication when required
- ✅ Run servers in isolated environments

## 🔗 Server Discovery

### Finding MCP Servers
1. **Official MCP Servers**: https://github.com/modelcontextprotocol/servers
2. **Community Servers**: Search GitHub for "MCP server"
3. **Your Own**: Build custom servers with LMCP's server tools

### Popular Server Types
- **File Operations**: filesystem, git, database
- **API Integration**: REST APIs, GraphQL, webhooks  
- **Development Tools**: linters, formatters, test runners
- **AI/ML**: model serving, data processing, embeddings
- **System Tools**: docker, kubernetes, monitoring

## 🎉 Start Using MCP Servers Today!

```python
# 1. Pick any MCP server
# 2. One line to connect
# 3. Natural Python API
# 4. That's it!

import asyncio
from lmcp import connect

async def main():
    async with connect("stdio://your-favorite-mcp-server") as client:
        tools = await client.list_tools()
        print(f"🎯 Ready to use {len(tools)} tools!")
        
        # Use any tool like a Python function
        result = await client.tools.amazing_feature(param="value")
        print(f"✨ Result: {result.content}")

asyncio.run(main())
```

**The entire MCP ecosystem is now at your fingertips!** 🚀