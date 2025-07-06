# LMCP - MCP Client Guide

LMCP is a simple MCP client for discovering and using existing MCP servers.

## Installation

```bash
# Clone and install from GitHub
git clone https://github.com/lhassa8/LMCP.git
cd LMCP

# Create and activate virtual environment
python -m venv lmcp-env
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate

# Install LMCP
pip install -e .
```

> ⚠️ **Always activate your virtual environment before using LMCP:**
> ```bash
> source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate
> ```

## Quick Start

```bash
# List available MCP servers
lmcp list

# Install a server
lmcp install filesystem

# Test if server works  
lmcp test filesystem

# Use a tool
lmcp use filesystem list_directory --params '{"path": "."}'
```

## Available Commands

- `lmcp list` - List all available MCP servers
- `lmcp install <server>` - Install an MCP server  
- `lmcp test <server>` - Test if a server is working
- `lmcp examples <server>` - Show usage examples for a server
- `lmcp use <server> <tool> --params <json>` - Call a tool on a server
- `lmcp version` - Show version information

## Available Servers (18 Total)

### Verified Working ✅
- **filesystem** - File operations (read, write, list files) - 12 tools
- **hello-world** - Simple Hello World MCP server for testing - 3 tools
- **sequential-thinking** - Sequential thinking and problem solving tools - 1 tool 
- **wikipedia** - Wikipedia API interactions and search - 4 tools

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

## Requirements

- Node.js and npm (for installing MCP servers)
- Python 3.8+

## Focus

LMCP focuses solely on:
1. **Discovering** existing MCP servers
2. **Installing** MCP servers via npm
3. **Using** MCP servers as a client

No server creation - just client functionality!