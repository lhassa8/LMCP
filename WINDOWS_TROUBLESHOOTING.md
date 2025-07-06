# Windows Troubleshooting Guide

This guide helps resolve common issues when using LMCP on Windows.

## Common Issues and Solutions

### 1. "npx command not found" Error

**Problem**: When running `lmcp discover test filesystem`, you get an error about npx not being found.

**Solution**:
1. Install Node.js from https://nodejs.org/
2. Restart your command prompt/terminal
3. Verify installation: `npx --version`
4. Install the filesystem server: `lmcp discover install filesystem`

### 2. "Connection attempt Failed" with stdio:// servers

**Problem**: MCP servers fail to connect with "Unsupported scheme" or connection errors.

**Solution**:
1. Ensure Node.js is properly installed
2. Check that the MCP server package is installed globally:
   ```bash
   npm list -g @modelcontextprotocol/server-filesystem
   ```
3. If not installed, run:
   ```bash
   lmcp discover install filesystem
   ```

### 3. Command Line Path Issues

**Problem**: Commands work in one terminal but not another.

**Solution**:
1. Restart your terminal after installing Node.js
2. Verify PATH includes Node.js:
   ```bash
   where npx
   ```
3. If using PowerShell, try Command Prompt or vice versa

### 4. Permission Errors

**Problem**: Permission denied when installing packages globally.

**Solution**:
1. Run terminal as Administrator
2. Or configure npm to use a different directory:
   ```bash
   npm config set prefix %APPDATA%\npm
   ```

### 5. Firewall/Antivirus Issues

**Problem**: Connections blocked by security software.

**Solution**:
1. Temporarily disable antivirus/firewall
2. Add Python and Node.js to firewall exceptions
3. Add the LMCP directory to antivirus exclusions

## Verification Steps

Run these commands to verify your setup:

```bash
# 1. Check Python
python --version

# 2. Check Node.js
node --version
npx --version

# 3. Check LMCP installation
lmcp --version

# 4. List available servers
lmcp discover list-available

# 5. Install and test a server
lmcp discover install filesystem
lmcp discover test filesystem
```

## Windows-Specific Notes

### PowerShell vs Command Prompt

- Some commands may work better in Command Prompt than PowerShell
- If you encounter issues, try switching terminals

### Path Separators

- Windows uses backslashes (`\`) for paths
- LMCP automatically handles path conversion
- Use forward slashes (`/`) in configuration files

### Environment Variables

- Node.js installation should automatically update PATH
- If not, manually add: `%APPDATA%\npm` to your PATH

## Getting Help

If you're still having issues:

1. Check the main [README.md](README.md) for general troubleshooting
2. Run commands with verbose output:
   ```bash
   lmcp --verbose discover test filesystem
   ```
3. Report issues at: https://github.com/lhassa8/LMCP/issues

Include this information in bug reports:
- Windows version
- Python version
- Node.js version
- Complete error message
- Steps to reproduce