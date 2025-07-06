# LMCP - MCP Client

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple MCP client for discovering and using existing MCP servers.

> 🚀 **New to MCP?** This tool helps you **use** existing MCP servers - no complex setup required!

## 🤔 What is MCP?

**Model Context Protocol (MCP)** lets AI assistants like Claude connect to external tools and data sources. Think of it as "plugins for AI" - MCP servers provide specific capabilities like file operations, web search, database access, etc.

**LMCP is a client** that makes it easy to discover and use these existing MCP servers without complex setup.

## ✨ Features

- **🔍 Server Discovery** - Find and catalog existing MCP servers
- **📦 Easy Installation** - Install MCP servers via npm with one command
- **🧪 Server Testing** - Test if servers work before using them
- **🔧 Tool Execution** - Call tools on MCP servers with simple commands
- **✅ Verified Servers** - Curated list of working MCP servers

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

# 4. Install a server (requires Node.js/npm)
lmcp install filesystem

# 5. Test if server works  
lmcp test filesystem

# 6. Use a tool
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

## 🎯 Focus

LMCP focuses solely on MCP **client** functionality:

✅ **Discovering** existing MCP servers  
✅ **Installing** MCP servers via npm  
✅ **Testing** server connectivity  
✅ **Using** MCP servers as a client  

❌ No server creation - just client functionality!

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Complete beginner guide (start here!)
- **[CLIENT_GUIDE.md](CLIENT_GUIDE.md)** - Detailed usage guide
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Official MCP specification

## 🤝 Contributing

We welcome contributions! Please open issues or submit PRs to expand our server catalog.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🔍 Discover → 📦 Install → 🧪 Test → 🔧 Use**