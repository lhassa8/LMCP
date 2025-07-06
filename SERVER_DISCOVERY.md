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

Currently indexed: **40+ servers** (12 verified, 30+ community)

### 📁 File System & Content
- **filesystem** - File operations (read, write, list, search)
- **fetch** - Web content fetching and conversion

### 🔧 Version Control
- **git** - Git operations (status, log, diff, blame)
- **github** - GitHub API access

### 🗄️ Database & Storage
- **postgres** - PostgreSQL operations
- **sqlite** - SQLite operations
- **mongodb** - MongoDB document operations
- **redis** - Redis cache operations
- **mysql** - MySQL database operations
- **elasticsearch** - Search and analytics

### ☁️ Cloud & DevOps
- **aws** - Amazon Web Services integration
- **azure** - Microsoft Azure services
- **docker** - Container management
- **kubernetes** - Cluster orchestration

### 🤖 AI & ML Tools
- **memory** - Knowledge graph persistence
- **openai** - OpenAI API integration
- **anthropic** - Claude API integration
- **huggingface** - Model inference & datasets

### 💬 Communication & Social
- **slack** - Slack workspace operations
- **discord** - Discord bot operations
- **telegram** - Telegram bot integration
- **teams** - Microsoft Teams collaboration

### 🛠️ Development & Project Management
- **linear** - Linear issue tracking
- **jira** - Atlassian Jira integration
- **asana** - Task management
- **notion** - Workspace operations
- **airtable** - Database management
- **trello** - Board management

### 🔍 Search & Knowledge
- **brave-search** - Web search
- **google-search** - Google Custom Search
- **wikipedia** - Wikipedia content
- **bing** - Microsoft Bing search

### 💰 Finance & E-commerce
- **stripe** - Payment processing
- **paypal** - Payment management
- **shopify** - E-commerce operations

### ⚙️ Code Execution & Analysis
- **python-sandbox** - Secure Python execution
- **node-sandbox** - Secure Node.js execution
- **bash-sandbox** - Secure shell commands
- **puppeteer** - Web scraping/automation

### 📧 Email & Calendar
- **gmail** - Gmail operations
- **outlook** - Outlook integration
- **calendar** - Google Calendar events

### 🛠️ Utilities
- **time** - Time and timezone operations

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

The current registry is just the beginning! We're working on:

- 🔍 **Auto-discovery** from GitHub/npm
- 🌐 **Community registry** with 100+ servers  
- 📦 **Custom registries** for organizations
- 🤖 **AI-powered server recommendations**

**Want to help expand the registry?** Check the [Contributing Guide](CONTRIBUTING.md) or open an issue with server suggestions!