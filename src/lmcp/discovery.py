"""
MCP Server Discovery System

Helps users find, install, and use existing MCP servers easily.
"""

import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ServerInfo:
    """Information about a discoverable MCP server."""
    name: str
    description: str
    repository: str
    install_command: str
    run_command: str
    category: str
    tags: List[str]
    tools: List[str]
    resources: List[str] = None
    examples: List[str] = None
    verified: bool = False
    
class MCPServerRegistry:
    """Registry of known MCP servers."""
    
    def __init__(self):
        self.servers = self._load_builtin_servers()
        self._load_extended_servers()
    
    def _load_builtin_servers(self) -> Dict[str, ServerInfo]:
        """Load the built-in registry of popular MCP servers."""
        
        servers = {
            "filesystem": ServerInfo(
                name="filesystem",
                description="Safe filesystem operations - read, write, list files and directories",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-filesystem",
                run_command="npx @modelcontextprotocol/server-filesystem /path/to/directory",
                category="file-system",
                tags=["files", "directories", "filesystem", "official"],
                tools=["read_file", "write_file", "read_directory", "create_directory", "move_file", "search_files"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-filesystem ./') as fs:",
                    "    files = await fs.tools.read_directory(path='.')",
                    "    content = await fs.tools.read_file(path='README.md')"
                ],
                verified=True
            ),
            
            "git": ServerInfo(
                name="git",
                description="Git operations - status, log, diff, commit history",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-git",
                run_command="npx @modelcontextprotocol/server-git",
                category="version-control",
                tags=["git", "version-control", "repository", "official"],
                tools=["git_status", "git_log", "git_diff", "git_show", "git_blame"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-git') as git:",
                    "    status = await git.tools.git_status()",
                    "    log = await git.tools.git_log(limit=10)"
                ],
                verified=True
            ),
            
            "postgres": ServerInfo(
                name="postgres",
                description="PostgreSQL database operations and queries",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-postgres",
                run_command="npx @modelcontextprotocol/server-postgres postgresql://user:pass@host:port/db",
                category="database",
                tags=["database", "postgresql", "sql", "official"],
                tools=["query", "list_tables", "describe_table", "list_schemas"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-postgres postgresql://...') as db:",
                    "    tables = await db.tools.list_tables()",
                    "    result = await db.tools.query(sql='SELECT * FROM users LIMIT 10')"
                ],
                verified=True
            ),
            
            "sqlite": ServerInfo(
                name="sqlite",
                description="SQLite database operations and queries",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-sqlite",
                run_command="npx @modelcontextprotocol/server-sqlite /path/to/database.db",
                category="database", 
                tags=["database", "sqlite", "sql", "official"],
                tools=["query", "list_tables", "describe_table", "create_table"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-sqlite ./data.db') as db:",
                    "    tables = await db.tools.list_tables()",
                    "    result = await db.tools.query(sql='SELECT count(*) FROM users')"
                ],
                verified=True
            ),
            
            "brave-search": ServerInfo(
                name="brave-search",
                description="Web search using Brave Search API",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-brave-search",
                run_command="npx @modelcontextprotocol/server-brave-search",
                category="search",
                tags=["search", "web", "brave", "api", "official"],
                tools=["web_search"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-brave-search') as search:",
                    "    results = await search.tools.web_search(query='MCP Model Context Protocol')"
                ],
                verified=True
            ),
            
            "github": ServerInfo(
                name="github",
                description="GitHub repository operations and API access",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-github",
                run_command="npx @modelcontextprotocol/server-github",
                category="development",
                tags=["github", "api", "repository", "issues", "official"],
                tools=["create_repository", "get_repository", "list_issues", "create_issue", "search_repositories"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-github') as github:",
                    "    repo = await github.tools.get_repository(owner='user', repo='project')",
                    "    issues = await github.tools.list_issues(owner='user', repo='project')"
                ],
                verified=True
            ),
            
            "puppeteer": ServerInfo(
                name="puppeteer",
                description="Web scraping and browser automation with Puppeteer",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-puppeteer",
                run_command="npx @modelcontextprotocol/server-puppeteer",
                category="web-scraping",
                tags=["puppeteer", "scraping", "browser", "automation", "official"],
                tools=["navigate", "screenshot", "get_page_content", "click_element", "fill_form"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-puppeteer') as browser:",
                    "    await browser.tools.navigate(url='https://example.com')",
                    "    content = await browser.tools.get_page_content()"
                ],
                verified=True
            ),
            
            "slack": ServerInfo(
                name="slack",
                description="Slack workspace operations and messaging",
                repository="https://github.com/modelcontextprotocol/servers",
                install_command="npm install -g @modelcontextprotocol/server-slack",
                run_command="npx @modelcontextprotocol/server-slack",
                category="communication",
                tags=["slack", "messaging", "communication", "workspace", "official"],
                tools=["send_message", "list_channels", "get_channel_history", "upload_file"],
                examples=[
                    "async with connect('stdio://npx @modelcontextprotocol/server-slack') as slack:",
                    "    await slack.tools.send_message(channel='#general', text='Hello team!')",
                    "    channels = await slack.tools.list_channels()"
                ],
                verified=True
            )
        }
        
        return servers
    
    def _load_extended_servers(self) -> None:
        """Load extended servers from the extended registry."""
        try:
            from .extended_registry import get_extended_servers
            extended_servers = get_extended_servers()
            self.servers.update(extended_servers)
        except ImportError:
            # Extended registry not available, skip
            pass
    
    def search(self, query: str = "", category: str = "", tags: List[str] = None) -> List[ServerInfo]:
        """Search for servers by query, category, or tags."""
        results = []
        query_lower = query.lower()
        tags = tags or []
        
        for server in self.servers.values():
            # Check query match
            if query and not any(query_lower in field.lower() for field in [
                server.name, server.description, " ".join(server.tags)
            ]):
                continue
            
            # Check category match
            if category and server.category != category:
                continue
                
            # Check tags match
            if tags and not any(tag in server.tags for tag in tags):
                continue
                
            results.append(server)
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(set(server.category for server in self.servers.values()))
    
    def get_by_name(self, name: str) -> Optional[ServerInfo]:
        """Get server info by name."""
        return self.servers.get(name)

async def test_server_availability(server_info: ServerInfo, timeout: float = 5.0) -> Dict[str, Any]:
    """Test if a server is available and working."""
    from .client import connect
    from .exceptions import ConnectionError
    import shutil
    import platform
    
    result = {
        "available": False,
        "error": None,
        "tools": [],
        "test_time": None
    }
    
    try:
        import time
        start_time = time.time()
        
        # Prepare the run command with proper path substitution
        run_command = server_info.run_command.replace("/path/to/directory", ".").replace("/path/to/database.db", "./test.db")
        
        # For Windows, check if npx is available
        if platform.system() == "Windows" and run_command.startswith("npx "):
            if not shutil.which("npx"):
                result["error"] = "npx command not found. Please install Node.js and npm first."
                return result
        
        # Add stdio:// prefix if not present
        if not run_command.startswith("stdio://"):
            run_command = f"stdio://{run_command}"
        
        # Try to connect with timeout
        async with connect(run_command) as client:
            tools = await client.list_tools()
            result["available"] = True
            result["tools"] = [t.name for t in tools]
            result["test_time"] = time.time() - start_time
            
    except ConnectionError as e:
        error_msg = str(e)
        if "Unsupported scheme" in error_msg:
            result["error"] = f"Connection failed: Invalid URI scheme. Expected stdio://, http://, or ws://"
        elif "npx" in error_msg and platform.system() == "Windows":
            result["error"] = "npx command failed. Please ensure Node.js and the MCP server package are installed."
        else:
            result["error"] = f"Connection failed: {error_msg}"
    except Exception as e:
        result["error"] = f"Test failed: {str(e)}"
    
    return result

async def install_server(server_info: ServerInfo) -> Dict[str, Any]:
    """Install a server using its install command."""
    result = {
        "success": False,
        "output": "",
        "error": None
    }
    
    try:
        # Run install command
        process = await asyncio.create_subprocess_shell(
            server_info.install_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            result["success"] = True
            result["output"] = stdout.decode()
        else:
            result["error"] = stderr.decode()
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

def get_server_examples(server_name: str) -> List[str]:
    """Get usage examples for a server."""
    registry = MCPServerRegistry()
    server = registry.get_by_name(server_name)
    
    if server and server.examples:
        return server.examples
    
    # Generate basic example
    return [
        f"async with connect('stdio://{server.run_command}') as client:",
        "    tools = await client.list_tools()",
        "    # Use any available tool",
        "    # result = await client.tools.tool_name(params)"
    ]

# CLI-friendly functions
def list_servers(category: str = "", search: str = "") -> List[Dict[str, Any]]:
    """List available servers in a CLI-friendly format."""
    registry = MCPServerRegistry()
    servers = registry.search(query=search, category=category)
    
    return [
        {
            "name": server.name,
            "description": server.description,
            "category": server.category,
            "tags": server.tags,
            "verified": server.verified,
            "install": server.install_command,
            "run": server.run_command
        }
        for server in servers
    ]

def get_categories() -> List[str]:
    """Get all server categories."""
    registry = MCPServerRegistry()
    return registry.get_categories()

def get_server_info(name: str) -> Optional[Dict[str, Any]]:
    """Get detailed info about a specific server."""
    registry = MCPServerRegistry()
    server = registry.get_by_name(name)
    
    if not server:
        return None
    
    return {
        "name": server.name,
        "description": server.description,
        "repository": server.repository,
        "category": server.category,
        "tags": server.tags,
        "tools": server.tools,
        "resources": server.resources or [],
        "install_command": server.install_command,
        "run_command": server.run_command,
        "examples": server.examples or [],
        "verified": server.verified
    }