# 🚀 LMCP Quick Start - Complete Beginner Guide

## Step 1: Install Prerequisites

### Install Python 3.8+
- **Windows/Mac**: Download from https://www.python.org/downloads/
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

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

# Install LMCP
pip install -e .

# Test installation
lmcp --help
```

## Step 3: Try Your First MCP Server

```bash
# See all available servers
lmcp list

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
pip install --user -e .
```

### "npm: command not found"
Install Node.js from https://nodejs.org/

## What's Next?

- Run `lmcp list` to see all 18 available servers
- Try different servers that don't require API keys
- Check out the full [CLIENT_GUIDE.md](CLIENT_GUIDE.md) for more details

## Need Help?

- Check [README.md](README.md) for full documentation
- File issues at https://github.com/lhassa8/LMCP/issues

---
**🎯 Goal**: Discover and use existing MCP servers easily!