# LMCP - MCP Client

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple MCP client for discovering and using existing MCP servers.

## ✨ Features

- **🔍 Server Discovery** - Find and catalog existing MCP servers
- **📦 Easy Installation** - Install MCP servers via npm with one command
- **🧪 Server Testing** - Test if servers work before using them
- **🔧 Tool Execution** - Call tools on MCP servers with simple commands
- **✅ Verified Servers** - Curated list of working MCP servers

## 🚀 Quick Start

```bash
# Install LMCP
pip install lmcp

# List available MCP servers
lmcp list

# Install a server (requires Node.js/npm)
lmcp install filesystem

# Test if server works  
lmcp test filesystem

# Use a tool
lmcp use filesystem list_directory --params '{"path": "."}'
```

## 🌐 Available Servers (18 Total)

### Verified Working ✅
- **filesystem** - File operations (read, write, list files)
- **hello-world** - Simple Hello World MCP server for testing (3 tools)
- **sequential-thinking** - Sequential thinking and problem solving tools (1 tool)
- **wikipedia** - Wikipedia API interactions and search (4 tools)

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

### List all available servers
```bash
lmcp list
```

### Install and test a server
```bash
lmcp install filesystem
lmcp test filesystem
```

### Use server tools
```bash
# Filesystem operations
lmcp use filesystem list_directory --params '{"path": "."}'
lmcp use filesystem read_file --params '{"path": "README.md"}'

# Hello World testing
lmcp use hello-world echo --params '{"message": "Hello LMCP!"}'

# Wikipedia search
lmcp use wikipedia findPage --params '{"query": "artificial intelligence"}'

# Get Wikipedia page content
lmcp use wikipedia getPage --params '{"title": "Python (programming language)"}'
```

## 📦 Installation

```bash
pip install lmcp
```

### Requirements
- Python 3.8+
- Node.js and npm (for installing MCP servers)

## 🎯 Focus

LMCP focuses solely on MCP **client** functionality:

✅ **Discovering** existing MCP servers  
✅ **Installing** MCP servers via npm  
✅ **Testing** server connectivity  
✅ **Using** MCP servers as a client  

❌ No server creation - just client functionality!

## 📚 Documentation

- **[Client Guide](CLIENT_GUIDE.md)** - Complete usage guide
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Official MCP specification

## 🤝 Contributing

We welcome contributions! Please open issues or submit PRs to expand our server catalog.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🔍 Discover → 📦 Install → 🧪 Test → 🔧 Use**