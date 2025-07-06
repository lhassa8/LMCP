# LMCP - MCP Client Guide

LMCP is a simple MCP client for discovering and using existing MCP servers.

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
- `lmcp use <server> <tool> --params <json>` - Call a tool on a server
- `lmcp version` - Show version information

## Available Servers

### Verified Servers ✅
- **filesystem** - File operations (read, write, list files)

### Community Servers ⚠️  
- **desktop-commander** - Terminal operations and file editing
- **gmail** - Gmail operations with auto authentication
- **figma** - Figma design operations
- **jsonresume** - JSON Resume operations
- **filesystem-secure** - Secure filesystem with relative path support
- **filesystem-advanced** - Advanced file operations with search and replace
- **supergateway** - Run MCP stdio servers over SSE/HTTP

## Requirements

- Node.js and npm (for installing MCP servers)
- Python 3.8+

## Focus

LMCP focuses solely on:
1. **Discovering** existing MCP servers
2. **Installing** MCP servers via npm
3. **Using** MCP servers as a client

No server creation - just client functionality!