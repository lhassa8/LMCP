#!/usr/bin/env python3
"""
Real-World LMCP Client Examples

Demonstrates practical patterns for using LMCP to connect to popular MCP servers.
These examples show how easy it is to integrate existing MCP servers into your projects.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
from lmcp import connect
from lmcp.exceptions import ConnectionError, ToolNotFoundError
from lmcp.types import ConnectionConfig

# Set up clean logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

async def filesystem_client_example():
    """
    Example: Using the MCP Filesystem Server
    
    The filesystem server provides safe file operations.
    Install: npm install @modelcontextprotocol/server-filesystem
    """
    print("\n📁 === Filesystem Client Example ===")
    
    # Common filesystem server URIs
    server_uris = [
        "stdio://npx @modelcontextprotocol/server-filesystem /path/to/dir",
        "stdio://mcp-server-filesystem",  # if installed globally
        "stdio://node filesystem-server.js"  # if you have a local copy
    ]
    
    # Try to connect to available filesystem server
    for uri in server_uris:
        try:
            print(f"🔌 Trying to connect to filesystem server...")
            
            # Try to connect with timeout
            async with connect(uri) as fs:
                print(f"✅ Connected to filesystem server!")
                
                # List available tools
                tools = await fs.list_tools()
                print(f"🛠️ Available tools: {[t.name for t in tools]}")
                
                # Example operations (would work with real server)
                """
                # Read current directory
                files = await fs.tools.read_directory(path=".")
                print(f"📋 Files: {files.content}")
                
                # Read a file safely
                if Path("README.md").exists():
                    content = await fs.tools.read_file(path="README.md")
                    print(f"📄 README preview: {content.content[:100]}...")
                
                # Write to a file (if permissions allow)
                await fs.tools.write_file(
                    path="test.txt", 
                    content="Hello from LMCP!"
                )
                """
                
                break
                
        except ConnectionError:
            print(f"❌ Could not connect to {uri}")
            continue
    else:
        print("💡 No filesystem server found. Install with:")
        print("   npm install @modelcontextprotocol/server-filesystem")

async def git_client_example():
    """
    Example: Using the MCP Git Server
    
    The git server provides safe git operations.
    Install: npm install @modelcontextprotocol/server-git
    """
    print("\n🔧 === Git Client Example ===")
    
    git_uris = [
        "stdio://npx @modelcontextprotocol/server-git",
        "stdio://mcp-server-git",
        "stdio://node git-server.js"
    ]
    
    for uri in git_uris:
        try:
            async with connect(uri) as git:
                print(f"✅ Connected to git server!")
                
                tools = await git.list_tools()
                print(f"🛠️ Git tools: {[t.name for t in tools]}")
                
                # Example git operations (would work with real server)
                """
                # Get git status
                status = await git.tools.git_status()
                print(f"📊 Git status: {status.content}")
                
                # Get commit log
                log = await git.tools.git_log(limit=5)
                print(f"📜 Recent commits: {log.content}")
                
                # Get diff
                diff = await git.tools.git_diff()
                print(f"🔍 Changes: {diff.content}")
                """
                
                break
                
        except ConnectionError:
            continue
    else:
        print("💡 No git server found. Install with:")
        print("   npm install @modelcontextprotocol/server-git")

async def database_client_example():
    """
    Example: Using a Database MCP Server
    
    Shows how to work with database servers.
    """
    print("\n🗄️ === Database Client Example ===")
    
    # Example with our advanced server or any database MCP server
    try:
        async with connect("stdio://python examples/advanced_server.py") as db:
            print("✅ Connected to database server!")
            
            # Discover capabilities
            tools = await db.list_tools()
            resources = await db.list_resources()
            
            print(f"🛠️ Database tools: {len(tools)}")
            print(f"📁 Resources: {len(resources)}")
            
            # Example database operations
            """
            # Create a user
            user = await db.tools.create_user(
                username="johndoe",
                email="john@example.com"
            )
            
            # Create a post
            post = await db.tools.create_post(
                user_id=user.content["id"],
                title="My First Post",
                content="Hello, MCP world!"
            )
            
            # Query posts
            posts = await db.tools.get_posts(limit=10)
            
            # Get analytics
            stats = await db.resources.get("analytics://user-stats")
            """
            
    except ConnectionError:
        print("💡 Database server not available. Check examples/advanced_server.py")

async def multi_server_client():
    """
    Example: Working with Multiple Servers
    
    Shows how to coordinate between different MCP servers.
    """
    print("\n🌐 === Multi-Server Client Example ===")
    
    # Example: Coordinating filesystem and git operations
    async def process_repository():
        """Process a git repository using both git and filesystem servers."""
        
        # Connect to multiple servers
        try:
            # This would work with real servers
            async with connect("stdio://npx @modelcontextprotocol/server-git") as git, \
                       connect("stdio://npx @modelcontextprotocol/server-filesystem .") as fs:
                
                print("✅ Connected to both git and filesystem servers!")
                
                # Get git status
                # status = await git.tools.git_status()
                
                # Read project files
                # files = await fs.tools.read_directory(path=".")
                
                # Combine information
                # return {
                #     "git_status": status.content,
                #     "files": files.content
                # }
                
                return {"demo": "Multi-server coordination"}
                
        except ConnectionError as e:
            print(f"❌ Multi-server connection failed: {e}")
            return None
    
    result = await process_repository()
    if result:
        print(f"📊 Coordinated result: {result}")

async def client_with_error_handling():
    """
    Example: Robust Error Handling
    
    Shows best practices for handling various error conditions.
    """
    print("\n🛡️ === Error Handling Example ===")
    
    from lmcp.exceptions import LMCPError, ServerError, ToolNotFoundError
    
    async def robust_operation(server_uri: str, tool_name: str, **kwargs):
        """Example of robust MCP operation with comprehensive error handling."""
        
        try:
            async with connect(server_uri) as client:
                
                # Check if tool exists
                tools = await client.list_tools()
                available_tools = [t.name for t in tools]
                
                if tool_name not in available_tools:
                    print(f"❌ Tool '{tool_name}' not available")
                    print(f"💡 Available tools: {available_tools}")
                    return None
                
                # Call the tool
                tool_func = getattr(client.tools, tool_name)
                result = await tool_func(**kwargs)
                
                if hasattr(result, 'is_error') and result.is_error:
                    print(f"❌ Tool error: {result.error_message}")
                    return None
                
                return result.content
                
        except ConnectionError as e:
            print(f"❌ Connection failed: {e}")
            return None
        except ToolNotFoundError as e:
            print(f"❌ Tool not found: {e}")
            return None
        except ServerError as e:
            print(f"❌ Server error: {e}")
            return None
        except LMCPError as e:
            print(f"❌ LMCP error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    # Test error handling
    result = await robust_operation(
        "stdio://nonexistent-server",
        "fake_tool",
        param="value"
    )
    
    print("✅ Error handling working correctly!")

async def client_performance_patterns():
    """
    Example: Performance Optimization Patterns
    
    Shows how to optimize client performance.
    """
    print("\n⚡ === Performance Patterns Example ===")
    
    # Pattern 1: Connection reuse
    async def batch_operations_same_server():
        """Reuse connection for multiple operations."""
        async with connect("stdio://python examples/basic_server.py") as calc:
            # Perform multiple operations efficiently
            operations = [
                calc.tools.add(a=i, b=i+1) 
                for i in range(5)
            ]
            
            # Execute in parallel
            results = await asyncio.gather(*operations, return_exceptions=True)
            
            successful = [r for r in results if not isinstance(r, Exception)]
            print(f"📊 Completed {len(successful)} operations")
    
    # Pattern 2: Parallel server connections
    async def parallel_servers():
        """Connect to multiple servers in parallel."""
        
        async def use_server(name: str, uri: str):
            try:
                async with connect(uri) as client:
                    tools = await client.list_tools()
                    return f"{name}: {len(tools)} tools"
            except:
                return f"{name}: unavailable"
        
        # Connect to multiple servers simultaneously
        tasks = [
            use_server("Calculator", "stdio://python examples/basic_server.py"),
            use_server("Database", "stdio://python examples/advanced_server.py"),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                print(f"❌ Server error: {result}")
            else:
                print(f"✅ {result}")
    
    print("🔄 Testing batch operations...")
    try:
        await batch_operations_same_server()
    except:
        print("💡 Calculator server not available for batch demo")
    
    print("🌐 Testing parallel servers...")
    await parallel_servers()

async def main():
    """Run all client examples."""
    print("🚀 Real-World LMCP Client Examples")
    print("=" * 50)
    print("These examples show how easy it is to use LMCP with existing MCP servers!")
    
    await filesystem_client_example()
    await git_client_example() 
    await database_client_example()
    await multi_server_client()
    await client_with_error_handling()
    await client_performance_patterns()
    
    print("\n" + "=" * 50)
    print("🎯 Key Takeaways:")
    print("  • LMCP makes any MCP server feel like a native Python library")
    print("  • Connection management is automatic with context managers")
    print("  • Tool discovery and calling is intuitive")
    print("  • Error handling is comprehensive and helpful")
    print("  • Performance patterns are straightforward")
    print("\n✨ Ready to integrate any MCP server into your Python projects!")

if __name__ == "__main__":
    asyncio.run(main())