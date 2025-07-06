# LMCP - Lightweight Model Context Protocol

[![PyPI version](https://badge.fury.io/py/lmcp.svg)](https://badge.fury.io/py/lmcp)
[![Python versions](https://img.shields.io/pypi/pyversions/lmcp.svg)](https://pypi.org/project/lmcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful yet easy-to-use Python wrapper for the Model Context Protocol (MCP). LMCP transforms the protocol-level MCP interface into a Pythonic, developer-friendly library that "just works" while maintaining full protocol capabilities.

## 🚀 Quick Start

### Installation
```bash
# Install from GitHub (current method)
pip install git+https://github.com/lhassa8/LMCP.git

# Coming soon: pip install lmcp
```

### Create a Server (super easy!)
```bash
# Create a sample server instantly
lmcp create sample my-calculator

# Run it 
python my_calculator_server.py
```

### Use Existing MCP Servers (super easy!)
```bash
# Discover available servers
lmcp discover list-available

# Get details about any server
lmcp discover info filesystem

# Install with one command
lmcp discover install filesystem

# Use immediately in Python
```
```python
async with lmcp.connect("stdio://npx @modelcontextprotocol/server-filesystem ./") as fs:
    files = await fs.tools.read_directory(path=".")
    content = await fs.tools.read_file(path="README.md")
```

That's it! Any MCP server becomes as easy as a Python library.

## ✨ Why LMCP?

- **🎯 Dead Simple**: `@lmcp.tool` decorator and you're done!
- **⚡ One-Line Connections**: `async with lmcp.connect("server://") as client:`
- **🌐 Server Discovery**: Find, install, and use any MCP server in seconds
- **🚀 Instant Servers**: Create servers from templates in seconds
- **🔧 Just Works**: Sensible defaults, auto-detection, error recovery
- **💪 Production Ready**: Connection pooling, middleware, monitoring
- **🐍 Pure Python**: Type hints, async/await, modern Python patterns

## ⚡ Get Started in 60 Seconds

```bash
# 1. Create a clean Python environment
python -m venv lmcp-env
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate

# 2. Install LMCP directly from GitHub
pip install git+https://github.com/lhassa8/LMCP.git

# 3. Create a server instantly
lmcp create sample my-tools

# 4. Test it immediately (no separate terminal needed!)
lmcp client list-tools "stdio://python my_tools_server.py"
lmcp client call-tool "stdio://python my_tools_server.py" add -a "a=10" -a "b=5"
```

**That's it!** You now have a working MCP server. 🎉

### Option 2: Development Install (If you have the repo)
```bash
# 1. Clone and enter the repository
git clone https://github.com/lhassa8/LMCP.git
cd LMCP

# 2. Quick setup (recommended)
python install_local.py

# 3. Activate and test
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate
python test_installation.py
```

### Option 3: Manual Development Install
```bash
# If you prefer manual setup
python -m venv lmcp-env
source lmcp-env/bin/activate
pip install -e .[dev]
python get_started.py
```

**That's it!** You now have a working MCP server. 🎉

> 💡 **Pro tip**: Always use a virtual environment to avoid dependency conflicts!

## 📦 Installation Options

```bash
# From GitHub (current method)
pip install git+https://github.com/lhassa8/LMCP.git

# Development install from local repo
pip install -e .

# With development tools (from repo)
pip install -e .[dev]

# With all examples (from repo)
pip install -e .[examples]
```

> 🚀 **Coming Soon**: LMCP will be published to PyPI for easier installation with `pip install lmcp`

## 🌐 Server Discovery - Use Any MCP Server Instantly

LMCP includes a powerful discovery system that makes finding and using existing MCP servers incredibly easy:

```bash
# See all available servers
lmcp discover list-available

# Get detailed info about any server
lmcp discover info filesystem

# Install any server with one command
lmcp discover install filesystem

# Test if it's working
lmcp discover test filesystem
```

**Available server categories:**
- 📁 **File System**: filesystem operations
- 🔧 **Version Control**: git operations  
- 🗄️ **Database**: postgres, sqlite operations
- 🌐 **Web & APIs**: github, brave-search, puppeteer
- 💬 **Communication**: slack operations

All servers include installation commands, usage examples, and are verified to work!

> 📚 **See [SERVER_DISCOVERY.md](SERVER_DISCOVERY.md) for the complete discovery guide**

## 💡 Common Use Cases (Copy & Paste!)

### Use Discovered Servers
```python
import lmcp

# Filesystem operations
async with lmcp.connect("stdio://npx @modelcontextprotocol/server-filesystem ./") as fs:
    files = await fs.tools.read_directory(path=".")
    content = await fs.tools.read_file(path="README.md")

# Git operations  
async with lmcp.connect("stdio://npx @modelcontextprotocol/server-git ./") as git:
    status = await git.tools.get_status()
    diff = await git.tools.get_diff()
```

### Create Servers in Seconds
```bash
# Interactive server creation
lmcp create server my-api --type api
lmcp create server my-db --type database
lmcp create sample calculator

# All generate ready-to-run Python files!
```

### Simple Server Creation

```python
import lmcp

@lmcp.server(name="calculator")
class Calculator:
    @lmcp.tool("Add two numbers")
    def add(self, a: int, b: int) -> int:
        """Add two integers together."""
        return a + b
    
    @lmcp.resource("Get calculator info")
    def info(self) -> dict:
        """Get calculator information."""
        return {"name": "Calculator", "version": "1.0.0"}

if __name__ == "__main__":
    lmcp.run_server(Calculator())
```

### Advanced Pipeline Usage

```python
import lmcp

async def main():
    async with lmcp.Pipeline() as pipeline:
        # Add multiple servers
        pipeline.add_server("filesystem://./docs")
        pipeline.add_server("git://./")
        
        # Add middleware
        pipeline.add_middleware(lmcp.CacheMiddleware())
        pipeline.add_middleware(lmcp.RetryMiddleware(max_retries=3))
        
        # Execute batch operations
        results = await pipeline.batch([
            ("filesystem.list_files", {"path": "."}),
            ("git.get_status", {}),
            ("filesystem.read_file", {"path": "package.json"})
        ])
        
        return results
```

## 🏗️ Architecture

LMCP provides three levels of abstraction:

1. **High-Level API**: Simple decorators and connection helpers
2. **Advanced Features**: Pipelines, middleware, and batch operations  
3. **Protocol-Level**: Direct access to MCP protocol details

```python
# Layer 1: Simple, high-level API
from lmcp import connect, Server, Tool

# Layer 2: Advanced features
from lmcp.advanced import Pipeline, Middleware, Streaming

# Layer 3: Protocol-level access
from lmcp.protocol import MCPClient, MCPServer
```

## 🛠️ Development

### Setup

```bash
git clone https://github.com/yourusername/LMCP.git
cd LMCP
pip install -e .[dev]
pre-commit install
```

### Testing

```bash
pytest                    # Run all tests
pytest tests/unit/       # Run unit tests only
pytest tests/integration/ # Run integration tests only
pytest -m "not slow"     # Skip slow tests
```

### Code Quality

```bash
black .                   # Format code
isort .                   # Sort imports
ruff .                    # Lint code
mypy .                    # Type checking
```

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Quick Start Tutorial](docs/quickstart.md)
- [API Reference](docs/api.md)
- [Advanced Usage](docs/advanced.md)
- [Examples](examples/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of [Anthropic's Model Context Protocol](https://modelcontextprotocol.io/)
- Inspired by the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## 🆘 Need Help?

- 📖 **Try It Now**: Run `python get_started.py` in this repo
- 🧪 **Examples**: Check the `examples/` folder 
- 💬 **CLI Help**: Run `lmcp --help` for all commands
- 🐛 **Issues**: Open an issue at https://github.com/lhassa8/LMCP/issues
- 📚 **Quick Reference**: See [QUICKSTART.md](QUICKSTART.md)

## 🔗 Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic](https://anthropic.com/)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)
- [GitHub Repository](https://github.com/lhassa8/LMCP)