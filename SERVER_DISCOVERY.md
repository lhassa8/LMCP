# 🌐 LMCP Server Discovery - Find and Use Any MCP Server

LMCP makes discovering and using existing MCP servers incredibly easy! No more hunting through GitHub or trying to figure out installation commands. With LMCP's built-in discovery system, you can find, install, and start using any MCP server in seconds.

## 🚀 Quick Start

```bash
# 1. See all available servers
lmcp discover list-available

# 2. Get details about any server
lmcp discover info filesystem

# 3. Install a server with one command
lmcp discover install filesystem

# 4. Test if it's working
lmcp discover test filesystem

# 5. Use it in your code immediately!
```

```python
async with connect('stdio://npx @modelcontextprotocol/server-filesystem ./') as fs:
    files = await fs.tools.read_directory(path='.')
    content = await fs.tools.read_file(path='README.md')
```

**That's it!** From discovery to usage in under 30 seconds! 🎉

## 🔍 Discovery Commands

### List All Available Servers
```bash
# Show all servers
lmcp discover list-available

# Show only verified servers
lmcp discover list-available --verified

# Filter by category
lmcp discover list-available --category database

# Search by keyword
lmcp discover list-available --search "file"
```

### Get Detailed Information
```bash
# Get complete info about a server
lmcp discover info filesystem

# This shows:
# • Description and capabilities
# • Installation command
# • Usage examples
# • Available tools and resources
# • Repository link
```

### Browse by Category
```bash
# See all categories
lmcp discover categories

# Browse servers in a category
lmcp discover list-available --category database
```

### Interactive Browse Mode
```bash
# Browse all servers interactively
lmcp discover browse

# Browse by category
lmcp discover browse --category development
```

## 📦 Installation and Testing

### Install Any Server
```bash
# One-command installation
lmcp discover install <server-name>

# Examples:
lmcp discover install filesystem
lmcp discover install git
lmcp discover install postgres
```

LMCP automatically runs the correct installation command for each server!

### Test Server Availability
```bash
# Check if a server is working
lmcp discover test filesystem

# This will:
# • Try to connect to the server
# • List available tools
# • Show connection time
# • Give you usage examples
```

## 🏪 Available Server Categories

LMCP includes a curated registry of popular MCP servers:

### 📁 **File System**
- **filesystem** - Safe file operations (read, write, list, search)

### 🔧 **Version Control** 
- **git** - Git operations (status, log, diff, blame)

### 🗄️ **Database**
- **postgres** - PostgreSQL database operations
- **sqlite** - SQLite database operations

### 🌐 **Web & APIs**
- **github** - GitHub repository operations
- **brave-search** - Web search using Brave Search
- **puppeteer** - Web scraping and automation

### 💬 **Communication**
- **slack** - Slack workspace operations

### 🧑‍💻 **Development**
- **github** - GitHub API access and operations

All servers are **verified** and include:
- ✅ Working installation commands
- 📚 Usage examples
- 🔧 Tool documentation
- 🔗 Repository links

## 💡 Real-World Usage Examples

### Example 1: File Operations
```bash
# 1. Discover and install
lmcp discover install filesystem

# 2. Use immediately
```
```python
async with connect('stdio://npx @modelcontextprotocol/server-filesystem ./') as fs:
    # List files
    files = await fs.tools.read_directory(path='.')
    
    # Read file content
    readme = await fs.tools.read_file(path='README.md')
    
    # Create new file
    await fs.tools.write_file(path='output.txt', content='Hello MCP!')
    
    # Search for files
    results = await fs.tools.search_files(pattern='*.py')
```

### Example 2: Git Operations
```bash
# 1. Install git server
lmcp discover install git

# 2. Use for repository analysis
```
```python
async with connect('stdio://npx @modelcontextprotocol/server-git') as git:
    # Get repository status
    status = await git.tools.git_status()
    
    # Get commit history
    log = await git.tools.git_log(limit=10)
    
    # Show differences
    diff = await git.tools.git_diff()
    
    # Blame analysis
    blame = await git.tools.git_blame(file_path='src/main.py')
```

### Example 3: Database Operations
```bash
# 1. Install database server
lmcp discover install postgres

# 2. Connect to your database
```
```python
async with connect('stdio://npx @modelcontextprotocol/server-postgres postgresql://user:pass@localhost/db') as db:
    # List tables
    tables = await db.tools.list_tables()
    
    # Run queries
    users = await db.tools.query(sql='SELECT * FROM users WHERE active = true')
    
    # Get table schema
    schema = await db.tools.describe_table(table_name='users')
```

### Example 4: Multi-Server Workflows
```python
# Use multiple servers together for powerful workflows
async with connect('stdio://npx @modelcontextprotocol/server-git') as git, \
           connect('stdio://npx @modelcontextprotocol/server-filesystem ./') as fs, \
           connect('stdio://npx @modelcontextprotocol/server-github') as github:
    
    # Get git status
    status = await git.tools.git_status()
    
    # Read project files
    package_json = await fs.tools.read_file(path='package.json')
    
    # Create GitHub issue if needed
    if status.content['dirty']:
        await github.tools.create_issue(
            owner='myuser',
            repo='myproject', 
            title='Uncommitted changes detected',
            body=f'Status: {status.content}'
        )
```

## 🎯 Discovery Workflow

Here's the typical workflow for discovering and using new MCP servers:

```bash
# 1. 🔍 Discover - See what's available
lmcp discover list-available

# 2. 📋 Learn - Get details about interesting servers  
lmcp discover info <server-name>

# 3. 📦 Install - One-command installation
lmcp discover install <server-name>

# 4. 🧪 Test - Verify it's working
lmcp discover test <server-name>

# 5. 🚀 Use - Start coding immediately!
```

## 🔧 Advanced Discovery Features

### Search and Filter
```bash
# Find servers by keyword
lmcp discover list-available --search "database"
lmcp discover list-available --search "file"
lmcp discover list-available --search "web"

# Filter by category
lmcp discover list-available --category database
lmcp discover list-available --category development

# Show only verified servers
lmcp discover list-available --verified
```

### Server Information
```bash
# Get complete details
lmcp discover info <server-name>

# This shows everything you need:
# • What the server does
# • How to install it
# • How to use it
# • Available tools
# • Code examples
# • Repository link
```

### Quick Testing
```bash
# Test server availability
lmcp discover test <server-name>

# Shows:
# • Connection status
# • Available tools
# • Response time
# • Usage examples
```

## 📚 Integration Patterns

### Pattern 1: Exploratory Development
```bash
# Explore what's available
lmcp discover categories
lmcp discover browse --category database

# Learn about options
lmcp discover info postgres
lmcp discover info sqlite

# Try them out
lmcp discover install postgres
lmcp discover test postgres
```

### Pattern 2: Project Setup
```bash
# Set up all servers for a project
lmcp discover install filesystem  # File operations
lmcp discover install git         # Version control
lmcp discover install github      # Repository management
lmcp discover install postgres    # Database

# Test everything works
lmcp discover test filesystem
lmcp discover test git
# ... etc
```

### Pattern 3: Learning and Documentation
```bash
# Learn about server capabilities
lmcp discover info <server-name>  # See tools and examples
lmcp discover test <server-name>   # See what tools are available

# Then use in development
async with connect('stdio://...') as client:
    tools = await client.list_tools()  # Discover tools programmatically
    # Use any tool...
```

## 🌟 Why LMCP Discovery is Awesome

### 🎯 **No More Hunting**
- No searching through GitHub repositories
- No reading complex installation docs
- No figuring out command line arguments

### ⚡ **Instant Setup**
- One command to install any server
- Automatic dependency management
- Immediate usage examples

### 🛡️ **Verified Quality**
- All servers are tested and verified
- Working installation commands guaranteed
- Comprehensive documentation included

### 🚀 **Immediate Productivity**
- From discovery to working code in 30 seconds
- Copy-paste ready examples
- Full integration with LMCP client features

## 🎉 Get Started Now!

```bash
# See what's available
lmcp discover list-available

# Pick something interesting
lmcp discover info filesystem

# Install and start using
lmcp discover install filesystem
lmcp discover test filesystem

# Start coding!
```

**The entire MCP ecosystem is now at your fingertips!** 🚀

No more barriers to using powerful MCP servers. With LMCP discovery, you can find, install, and start using any MCP server in seconds. Happy coding! ✨