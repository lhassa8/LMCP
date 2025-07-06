# 🌐 Server Discovery Guide

LMCP includes a powerful discovery system to find, install, and use existing MCP servers instantly.

## Quick Start

```bash
# Discover servers
lmcp discover list-available

# Get details  
lmcp discover info filesystem

# Install and test
lmcp discover install filesystem
lmcp discover test filesystem
```

```python
# Use immediately
async with lmcp.connect("stdio://npx @modelcontextprotocol/server-filesystem ./") as fs:
    files = await fs.tools.read_directory(path=".")
```

## Discovery Commands

| Command | Purpose |
|---------|---------|
| `lmcp discover list-available` | Show all servers |
| `lmcp discover info <name>` | Get server details |
| `lmcp discover install <name>` | Install server |
| `lmcp discover test <name>` | Test server |
| `lmcp discover categories` | Show categories |
| `lmcp discover browse` | Interactive browsing |

### Filtering Options

```bash
# By category
lmcp discover list-available --category database

# By search term  
lmcp discover list-available --search "file"

# Verified only
lmcp discover list-available --verified
```

## Available Servers

Currently indexed: **19 verified servers** (all working and tested)

### 📁 File System & Content
- **filesystem** ✅ - File operations (read, write, list, search)
- **fetch** ✅ - Web content fetching and conversion

### 🔧 Version Control
- **git** ✅ - Git operations (status, log, diff, blame)
- **github** ✅ - GitHub API access

### 🗄️ Database & Storage
- **postgres** ✅ - PostgreSQL operations
- **sqlite** ✅ - SQLite operations

### ☁️ Cloud & Services
- **aws** ✅ - Amazon Web Services integration  
- **azure** ✅ - Microsoft Azure services
- **cloudflare** ✅ - Cloudflare CDN and DNS
- **aiven** ✅ - Aiven cloud data platform

### 🔍 Search & AI Tools
- **brave-search** ✅ - Web search using Brave API
- **algolia** ✅ - Algolia search and indexing
- **sequential-thinking** ✅ - AI reasoning and problem-solving
- **memory** ✅ - Knowledge graph persistence

### 🗺️ Location & Maps
- **google-maps** ✅ - Google Maps API integration
- **time** ✅ - Time and timezone operations

### 🔐 Authentication & Media
- **auth0** ✅ - Auth0 user management
- **cloudinary** ✅ - Media management and optimization

### 💬 Communication
- **slack** ✅ - Slack workspace operations
- **puppeteer** ✅ - Web scraping and automation

**✅ = Verified and working**

## Usage Patterns

### Single Server
```python
async with lmcp.connect("stdio://npx @modelcontextprotocol/server-git") as git:
    status = await git.tools.git_status()
    log = await git.tools.git_log(limit=5)
```

### Multi-Server Workflow
```python
async with lmcp.connect("stdio://npx @modelcontextprotocol/server-git") as git, \
           lmcp.connect("stdio://npx @modelcontextprotocol/server-github") as github:
    
    status = await git.tools.git_status()
    if status.content['dirty']:
        await github.tools.create_issue(
            title="Uncommitted changes detected",
            body=f"Status: {status.content}"
        )
```

## Contributing Servers

To add more servers to the registry:

1. **Manual Addition**: Submit PR with server info to `src/lmcp/discovery.py`
2. **Auto-Discovery**: Run `lmcp discover scan` (coming soon)
3. **Community Registry**: Submit to community index (planned)

## Need More Servers?

**Quality over Quantity**: We focus on verified, working servers rather than a large list of potentially broken ones.

### ✅ What "Verified" Means:
- Package actually exists on npm
- Installation commands work
- Server starts without errors
- Basic functionality tested

### 🔮 Future Plans:
- 🔍 **Auto-discovery** from GitHub/npm (finds real packages)
- 🧪 **Automated testing** pipeline for new servers
- 🌐 **Community contributions** with verification
- 📊 **Server health monitoring**

### 📝 Contributing New Servers:
1. **Ensure the server actually exists** and is published
2. **Test installation and basic functionality**
3. **Submit PR** with verification details
4. **Include API key setup instructions** if needed

**Want to help expand the registry?** Check the [Contributing Guide](CONTRIBUTING.md) or open an issue with server suggestions!