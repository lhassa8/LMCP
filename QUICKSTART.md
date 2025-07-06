# 🚀 LMCP Quick Start - Complete Beginner Guide

## Step 1: Install Prerequisites

### Install Python 3.8+
- **Windows/Mac**: Download from https://www.python.org/downloads/
- **Linux**: `sudo apt install python3 python3-pip python3-venv` (Ubuntu/Debian)

> 💡 **Windows Users**: Make sure to check "Add Python to PATH" during installation!

### Install Node.js & npm  
- **All platforms**: Download from https://nodejs.org/
- Verify: Run `node --version` and `npm --version`

### Install Git
- **All platforms**: Download from https://git-scm.com/downloads/

## Step 2: Install LMCP

```bash
# Clone the repository
git clone https://github.com/lhassa8/LMCP.git

# Enter directory
cd LMCP

# Create virtual environment (IMPORTANT!)
python -m venv lmcp-env

# Activate virtual environment
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate

# Install LMCP
pip install -e .

# Test installation
lmcp --help
```

> 🔥 **Always activate your virtual environment first!**
> ```bash
> source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate
> ```

## Step 3: Try Your First MCP Server

> **Remember**: Make sure your virtual environment is active!
> ```bash
> source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate
> ```

```bash
# See all available servers
lmcp list

# Get examples for hello-world server
lmcp examples hello-world

# Install the hello-world server
lmcp install hello-world

# Test it works
lmcp test hello-world

# Use the echo tool
lmcp use hello-world echo --params '{"message": "Hello World!"}'
```

You should see: `"You said: Hello World!"`

## Step 4: Try More Servers

### Wikipedia Search
```bash
# Install Wikipedia server
lmcp install wikipedia
lmcp test wikipedia

# Search for articles
lmcp use wikipedia findPage --params '{"query": "python programming"}'
```

### File Operations
```bash
# Install filesystem server
lmcp install filesystem
lmcp test filesystem

# List files in current directory
lmcp use filesystem list_directory --params '{"path": "."}'
```

## Common Issues

### "pip: command not found"
```bash
python -m ensurepip --upgrade
```

### "Permission denied"
```bash
# Use virtual environment instead (recommended)
python -m venv lmcp-env
source lmcp-env/bin/activate
pip install -e .

# Or use --user flag as fallback
pip install --user -e .
```

### "npm: command not found"
Install Node.js from https://nodejs.org/

## Step 5: Using Python API (Optional)

If you want to use LMCP in your Python code instead of the CLI:

```python
import asyncio
from lmcp import SimpleMCP

async def python_example():
    # Create client
    client = SimpleMCP()
    
    # Install and test hello-world server
    client.install_server("hello-world")
    await client.test_server("hello-world")
    
    # Use a tool
    result = await client.call_tool("hello-world", "echo", message="Hello from Python!")
    print(f"Result: {result}")

# Run the example
asyncio.run(python_example())
```

> 📚 **Want more Python examples?** Check out [PYTHON_API.md](PYTHON_API.md) for comprehensive Python usage guide!

## What's Next?

- Run `lmcp list` to see all 18 available servers
- Try different servers that don't require API keys
- Check out the full [CLIENT_GUIDE.md](CLIENT_GUIDE.md) for more details
- Use [PYTHON_API.md](PYTHON_API.md) for programmatic usage

## Need Help?

- Check [README.md](README.md) for full documentation
- File issues at https://github.com/lhassa8/LMCP/issues

---
**🎯 Goal**: Discover and use existing MCP servers easily!