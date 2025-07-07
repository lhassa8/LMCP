# LMCP - MCP Client

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple MCP client for discovering and using existing MCP servers with **automatic tool discovery**.

> 🚀 **New to MCP?** This tool helps you **discover and use** existing MCP servers without guessing parameters!

## 🤔 What is MCP?

**Model Context Protocol (MCP)** lets AI assistants like Claude connect to external tools and data sources. Think of it as "plugins for AI" - MCP servers provide specific capabilities like file operations, web search, database access, etc.

**LMCP is a smart client** that automatically discovers tools and parameters, making any MCP server easy to use without guessing or reading documentation.

## 🚨 Solves the MCP Usability Problem

**The Problem:** Every MCP server works differently. Users have to guess parameter names, read documentation, or use trial-and-error to figure out how to use tools.

**The Solution:** LMCP automatically inspects servers and discovers:
- ✅ **All available tools** with descriptions
- ✅ **Required vs optional parameters** with types  
- ✅ **Auto-generated examples** for every tool
- ✅ **Real-time parameter hints** when something's missing

**Result:** No more guessing - use any MCP server immediately!

| Traditional MCP Usage | LMCP Smart Usage |
|---|---|
| ❌ Read docs to find tools | ✅ `lmcp inspect server` shows all tools |
| ❌ Guess parameter names | ✅ See exact required parameters |
| ❌ Trial and error with types | ✅ Auto-generated examples |
| ❌ Different servers, different rules | ✅ Works with ANY MCP server |

```bash
# Traditional way: ❌ Guess and hope
lmcp use server tool --params '{"mystery": "???"}'  # What parameters?!

# LMCP way: ✅ Discover and use
lmcp inspect server           # See all tools and exact parameters
lmcp use server tool --params '{"required_param": "value"}'  # Use with confidence!
```

## ✨ Key Features

- **🎯 Zero-Guessing Usage** - Automatically discover tools and required parameters from any MCP server
- **🔍 Smart Tool Inspection** - See all available tools with descriptions, parameters, and auto-generated examples  
- **🛡️ Parameter Validation** - Get helpful hints when parameters are missing or incorrect
- **📦 Easy Installation** - Install MCP servers via npm with one command
- **🧪 Server Testing** - Test if servers work before using them
- **🐍 Full Python API** - Complete programmatic access with discovery features
- **✅ 18+ Server Catalog** - Curated list of working MCP servers

## 🚀 Quick Start

> 📚 **Complete Beginner?** Check out [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions!

```bash
# 1. Clone and create virtual environment
git clone https://github.com/lhassa8/LMCP.git
cd LMCP
python -m venv lmcp-env
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate

# 2. Install LMCP
pip install -e .

# 3. List available MCP servers
lmcp list

# 4. Install a server (requires Node.js/npm) - Using Wikipedia as example
lmcp install wikipedia

# 5. Test if server works  
lmcp test wikipedia

# 6. 🔍 DISCOVER tools and parameters (No more guessing!)
lmcp inspect wikipedia
# Shows: findPage needs "query" (string), getPage needs "title" (string), etc.

# 7. ✅ Use tools with confidence  
lmcp use wikipedia findPage --params '{"query": "artificial intelligence"}'
```

## 🌐 Available Servers (18 Total)

> **Icon Legend:**
> - ✅ **Verified Working** - Tested and confirmed to work reliably
> - ⚠️ **Community Servers** - May require setup, credentials, or have compatibility issues

### Verified Working ✅
- **filesystem** - File operations (read, write, list files) - **ALL 12 tools work perfectly**
- **sequential-thinking** - Sequential thinking and problem solving tools - **1 tool works perfectly**
- **wikipedia** - Wikipedia API interactions and search - **3/4 tools work** (onThisDay broken)
- **hello-world** - Simple Hello World MCP server for testing - **2/3 tools work** (add broken)

### Community Servers ⚠️  
- **desktop-commander** - Terminal operations and file editing
- **gmail** - Gmail operations with auto authentication
- **figma** - Figma design operations
- **jsonresume** - JSON Resume operations
- **filesystem-secure** - Secure filesystem with relative path support
- **filesystem-advanced** - Advanced file operations with search and replace
- **supergateway** - Run MCP stdio servers over SSE/HTTP
- **calculator** - Calculator for precise numerical calculations
- **dad-jokes** - The one and only MCP Server for dad jokes
- **code-runner** - Code execution and running capabilities
- **kubernetes** - Kubernetes cluster interactions via kubectl
- **elasticsearch** - Elasticsearch search and indexing operations
- **basic-mcp** - Basic MCP server implementation
- **mysql** - MySQL database interactions

## 📖 Usage Examples

### Command Line Interface

#### List all available servers
```bash
lmcp list
```

#### Install and test a server
```bash
lmcp install wikipedia
lmcp test wikipedia
```

#### 🔍 Discover tools and parameters automatically (KEY FEATURE!)
```bash
# See ALL tools with parameters, types, and auto-generated examples
lmcp inspect wikipedia     # Shows 4 Wikipedia tools with exact parameter formats
lmcp inspect filesystem    # Shows 12 file operation tools  
lmcp inspect hello-world   # Shows 3 testing tools

# Example output:
# 🔧 findPage
#    📝 Search for Wikipedia pages matching a query
#    📥 Parameters:
#       • query (string) (required) - Search query
#    💡 Example: lmcp use wikipedia findPage --params '{"query": "example_query"}'
```

#### Get examples for any server (static examples)
```bash
# See curated examples for any server  
lmcp examples wikipedia
lmcp examples filesystem
lmcp examples hello-world
```

#### Use server tools
```bash
# Wikipedia search and information
lmcp use wikipedia findPage --params '{"query": "artificial intelligence"}'
lmcp use wikipedia getPage --params '{"title": "Python (programming language)"}'

# Filesystem operations
lmcp use filesystem list_directory --params '{"path": "."}'
lmcp use filesystem read_file --params '{"path": "README.md"}'

# Hello World testing
lmcp use hello-world echo --params '{"message": "Hello LMCP"}'
```

### Python API

Use LMCP programmatically with automatic tool discovery:

```python
import asyncio
from lmcp import SimpleMCP

async def main():
    # Create client
    client = SimpleMCP()
    
    # Install and test a server
    client.install_server("wikipedia")
    await client.test_server("wikipedia")
    
    # 🔍 DISCOVER tools and parameters automatically
    schema = await client.inspect_server("wikipedia")
    print("Available tools:", [tool['name'] for tool in schema['result']['tools']])
    
    # 🔍 Get specific tool requirements
    tool_schema = await client.get_tool_schema("wikipedia", "findPage")
    required_params = tool_schema['tool']['inputSchema']['required']
    print(f"findPage requires: {required_params}")
    
    # ✅ Use tools with confidence (no guessing!)
    result = await client.call_tool("wikipedia", "findPage", query="artificial intelligence")
    print("Search results:", result)

# Run the example
asyncio.run(main())
```

> 📚 **Full Python API Guide**: See [PYTHON_API.md](PYTHON_API.md) for comprehensive examples, error handling, and advanced usage patterns.

## 📦 Installation

### Prerequisites
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js and npm** - [Download here](https://nodejs.org/) (required for MCP servers)
- **Git** - [Download here](https://git-scm.com/downloads)

### Install from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/lhassa8/LMCP.git
cd LMCP

# Create and activate virtual environment
python -m venv lmcp-env
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate

# Install in development mode
pip install -e .

# Verify installation
lmcp --help
```

> ⚠️ **Important**: Always activate your virtual environment before using LMCP:
> ```bash
> source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate
> ```

### Alternative: Download ZIP
1. Go to https://github.com/lhassa8/LMCP
2. Click "Code" → "Download ZIP"
3. Extract, then:
   ```bash
   cd LMCP
   python -m venv lmcp-env
   source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate
   pip install -e .
   ```

### Troubleshooting Installation

**Issue: `lmcp: command not found`**
```bash
# Activate your virtual environment first!
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate
```

**Issue: `pip: command not found`**
```bash
# Install pip first
python -m ensurepip --upgrade
```

**Issue: Permission denied**
```bash
# Use virtual environment (recommended)
python -m venv lmcp-env
source lmcp-env/bin/activate
pip install -e .
```

**Issue: Node.js not found**
```bash
# Verify Node.js installation
node --version
npm --version
```

## 🎯 Core Capabilities

LMCP is a **smart MCP client** that solves the parameter guessing problem:

✅ **Auto-Discovery** - Inspect any MCP server to discover tools and parameters  
✅ **Zero-Guessing** - Never guess parameter names or types again  
✅ **Smart Validation** - Get helpful hints when parameters are missing  
✅ **Server Management** - Install, test, and use MCP servers easily  
✅ **Both CLI & Python** - Command-line and programmatic access  

❌ No server creation - just intelligent client functionality!

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Complete beginner guide (start here!)
- **[PYTHON_API.md](PYTHON_API.md)** - Comprehensive Python API guide with examples
- **[EXAMPLES.md](EXAMPLES.md)** - CLI usage examples for all 18 servers
- **[CLIENT_GUIDE.md](CLIENT_GUIDE.md)** - Detailed CLI usage guide
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Official MCP specification

## 🤝 Contributing

We welcome contributions! Please open issues or submit PRs to expand our server catalog.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🔍 Discover Servers → 📦 Install → 🧪 Test → 🔍 Inspect Tools → ✅ Use Without Guessing**