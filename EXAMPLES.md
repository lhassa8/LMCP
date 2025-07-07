# 📋 LMCP Server Examples

Complete usage examples for all MCP servers. Get examples for any server with:

```bash
lmcp examples <server-name>
```

## ✅ Verified Working Servers

### 🗂️ filesystem - File Operations
```bash
# List directory contents
lmcp use filesystem list_directory --params '{"path": "."}'

# Read a file
lmcp use filesystem read_file --params '{"path": "README.md"}'

# Write to a file
lmcp use filesystem write_file --params '{"path": "test.txt", "content": "Hello World"}'

# Create a directory
lmcp use filesystem create_directory --params '{"path": "new_folder"}'
```

### 👋 hello-world - Testing & Demo
```bash
# Echo a message
lmcp use hello-world echo --params '{"message": "Hello LMCP"}'

# Get debug information
lmcp use hello-world debug --params '{}'
```

### 📚 wikipedia - Wikipedia Search
```bash
# Search for articles
lmcp use wikipedia findPage --params '{"query": "artificial intelligence"}'

# Get page content
lmcp use wikipedia getPage --params '{"title": "Python (programming language)"}'

# Today in history  
lmcp use wikipedia onThisDay --params '{"date": "2025-07-06"}'
```

### 🤔 sequential-thinking - Problem Solving
```bash
# Think through a problem step by step
lmcp use sequential-thinking sequentialthinking --params '{"thought": "How to solve this problem", "thoughtNumber": 1, "totalThoughts": 3, "nextThoughtNeeded": true}'
```

## ⚠️ Community Servers

### 💻 desktop-commander - Terminal Operations
```bash
# Run terminal command
lmcp use desktop-commander exec --params '{"command": "ls -la"}'

# Edit file
lmcp use desktop-commander edit --params '{"file": "test.txt", "content": "Hello"}'
```

### 📧 gmail - Email Operations (Requires Auth)
```bash
# List emails
lmcp use gmail listEmails --params '{"maxResults": 10}'

# Send email
lmcp use gmail sendEmail --params '{"to": "example@domain.com", "subject": "Test", "body": "Hello"}'
```

### 🎨 figma - Design Operations (Requires Auth)
```bash
# Get file info
lmcp use figma getFile --params '{"fileId": "your-file-id"}'

# List projects
lmcp use figma getProjects --params '{}'
```

### 📄 jsonresume - Resume Operations
```bash
# Get resume
lmcp use jsonresume getResume --params '{}'

# Update resume
lmcp use jsonresume updateResume --params '{"section": "basics", "data": {}}'
```

### 🔒 filesystem-secure - Secure File Operations
```bash
# List directory (secure)
lmcp use filesystem-secure list --params '{"path": "."}'

# Read file (secure)
lmcp use filesystem-secure read --params '{"path": "README.md"}'
```

### 🔧 filesystem-advanced - Advanced File Operations
```bash
# Search and replace
lmcp use filesystem-advanced searchReplace --params '{"path": ".", "search": "old", "replace": "new"}'

# Batch operations
lmcp use filesystem-advanced batchOp --params '{"operation": "rename", "pattern": "*.txt"}'
```

### 🔢 calculator - Math Operations
```bash
# Basic calculation
lmcp use calculator calculate --params '{"expression": "2 + 2 * 3"}'
```

### 😄 dad-jokes - Humor
```bash
# Get random joke
lmcp use dad-jokes getJoke --params '{}'
```

### ▶️ code-runner - Code Execution
```bash
# Run Python code
lmcp use code-runner run --params '{"language": "python", "code": "print(\"Hello World\")"}'
```

### ☸️ kubernetes - Cluster Management (Requires kubectl)
```bash
# List pods
lmcp use kubernetes kubectl --params '{"command": "get pods"}'

# Get services
lmcp use kubernetes kubectl --params '{"command": "get services"}'
```

### 🗄️ mysql - Database Operations (Requires DB)
```bash
# Execute query
lmcp use mysql query --params '{"sql": "SELECT * FROM users LIMIT 5"}'
```

### 🔍 elasticsearch - Search Operations (Requires ES)
```bash
# Search index
lmcp use elasticsearch search --params '{"index": "my-index", "query": "test"}'

# Create document
lmcp use elasticsearch index --params '{"index": "my-index", "document": {"title": "Test"}}'
```

### 🌉 supergateway - HTTP Proxy
```bash
# Proxy request
lmcp use supergateway proxy --params '{"url": "http://localhost:3000", "method": "GET"}'
```

### 🔰 basic-mcp - Basic Operations
```bash
# Basic operation
lmcp use basic-mcp hello --params '{"name": "World"}'
```

## 💡 Tips

1. **Get Examples**: Always run `lmcp examples <server>` first
2. **Test First**: Run `lmcp test <server>` before using
3. **JSON Format**: Parameters must be valid JSON
4. **Escaping**: Use single quotes around JSON in bash
5. **Credentials**: Some servers require API keys or authentication

## 🚀 Quick Start

```bash
# Pick a server and get examples
lmcp list
lmcp examples hello-world

# Install and test
lmcp install hello-world
lmcp test hello-world

# Use it!
lmcp use hello-world echo --params '{"message": "Hello!"}'
```