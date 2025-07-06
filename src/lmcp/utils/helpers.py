"""
Helper functions to make LMCP super easy to use.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..server import Server, tool, resource
from ..client import connect


def auto_detect_servers() -> List[str]:
    """
    Auto-detect common MCP servers on the system.
    
    Returns:
        List of detected server URIs
    """
    detected = []
    
    # Common MCP servers to look for
    common_servers = [
        ("filesystem", "npx @modelcontextprotocol/server-filesystem ./"),
        ("git", "npx @modelcontextprotocol/server-git ./"),
        ("sqlite", "npx @modelcontextprotocol/server-sqlite"),
        ("brave-search", "npx @modelcontextprotocol/server-brave-search"),
        ("github", "npx @modelcontextprotocol/server-github"),
    ]
    
    for name, command in common_servers:
        # Check if npx is available (simple heuristic)
        try:
            import subprocess
            result = subprocess.run(["npx", "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                detected.append(f"stdio://{command}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return detected


async def simple_run(server_or_function, port: int = 8080) -> None:
    """
    Super simple way to run a server from a function or class.
    
    Args:
        server_or_function: Server instance, class, or function
        port: Port to run on
        
    Examples:
        >>> def my_tool(x: int) -> int:
        ...     return x * 2
        >>> simple_run(my_tool)
        
        >>> @tool("Double a number")
        ... def double(x: int) -> int:
        ...     return x * 2
        >>> simple_run(double)
    """
    from ..server import run_server
    
    # If it's already a server, just run it
    if isinstance(server_or_function, Server):
        await run_server(server_or_function)
        return
    
    # If it's a function, wrap it in a server
    if callable(server_or_function):
        # Create a simple server from the function
        class SimpleServer(Server):
            def __init__(self):
                super().__init__("simple-server")
                # Add the function as a tool
                if hasattr(server_or_function, '_lmcp_tool'):
                    # Already decorated
                    self._tool_registry.register(
                        server_or_function._lmcp_tool['name'],
                        server_or_function,
                        server_or_function._lmcp_tool['description']
                    )
                else:
                    # Not decorated, use function name
                    func_name = getattr(server_or_function, '__name__', 'tool')
                    self._tool_registry.register(
                        func_name,
                        server_or_function,
                        getattr(server_or_function, '__doc__', f"Execute {func_name}")
                    )
        
        server = SimpleServer()
        await run_server(server)
        return
    
    raise ValueError("server_or_function must be a Server instance or callable")


def create_sample_server(name: str = "sample-server") -> str:
    """
    Create a sample server file to get started quickly.
    
    Args:
        name: Name for the server
        
    Returns:
        Path to the created file
        
    Examples:
        >>> create_sample_server("my-tools")
        'my_tools_server.py'
    """
    filename = f"{name.replace('-', '_')}_server.py"
    
    content = f'''"""
{name.title()} MCP Server

A sample MCP server created with LMCP.
"""

import lmcp
import math

@lmcp.server("{name}")
class {name.replace('-', '').title()}Server:
    """Sample server with basic tools and resources."""
    
    @lmcp.tool("Add two numbers")
    def add(self, a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b
    
    @lmcp.tool("Calculate square root")
    def sqrt(self, x: float) -> float:
        """Calculate the square root of a number."""
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(x)
    
    @lmcp.tool("Generate greeting")
    def greet(self, name: str = "World") -> str:
        """Generate a friendly greeting."""
        return f"Hello, {{name}}! 👋"
    
    @lmcp.resource("server://info", description="Server information")
    def server_info(self) -> dict:
        """Get information about this server."""
        return {{
            "name": "{name}",
            "version": "1.0.0",
            "capabilities": ["math", "greetings"],
            "status": "running"
        }}
    
    @lmcp.resource("server://stats", description="Server statistics")
    def server_stats(self) -> dict:
        """Get server statistics."""
        return {{
            "tools": len(self.list_tools()),
            "resources": len(self.list_resources()),
            "uptime": "just started"
        }}

if __name__ == "__main__":
    import sys
    
    # Only show startup messages if not in stdio mode
    if sys.stdout.isatty():
        print("🚀 Starting {name} server...")
        print("📋 Available tools: add, sqrt, greet")
        print("📁 Available resources: server://info, server://stats")
        print("🌐 Use the LMCP CLI to test: lmcp client list-tools \"stdio://python {filename}\"")
        print()
    
    server = {name.replace('-', '').title()}Server()
    lmcp.run_server(server)
'''
    
    Path(filename).write_text(content)
    print(f"✅ Created sample server: {filename}")
    
    # Quick validation - try to import the server
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_server", filename)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✅ Server validation: Import successful")
        else:
            print("⚠️  Server validation: Could not load module")
    except Exception as e:
        print(f"⚠️  Server validation: {e}")
        print("💡 This might be normal if the server has external dependencies")
    
    print(f"🚀 Run with: python {filename}")
    print(f"🧪 Test with: lmcp client list-tools \"stdio://python {filename}\"")
    
    return filename


def quick_test_connection(uri: str) -> bool:
    """
    Quickly test if we can connect to a server.
    
    Args:
        uri: Server URI to test
        
    Returns:
        True if connection successful, False otherwise
    """
    async def _test():
        try:
            async with connect(uri) as client:
                await client.list_tools()
                return True
        except Exception:
            return False
    
    try:
        return asyncio.run(_test())
    except Exception:
        return False


def get_server_info(uri: str) -> Optional[Dict[str, Any]]:
    """
    Get basic information about a server.
    
    Args:
        uri: Server URI
        
    Returns:
        Server info dictionary or None if connection failed
    """
    async def _get_info():
        try:
            async with connect(uri) as client:
                info = client.server_info
                tools = await client.list_tools()
                resources = await client.list_resources()
                
                return {
                    "name": info.name if info else "Unknown",
                    "version": info.version if info else "Unknown", 
                    "description": info.description if info else None,
                    "tools": len(tools),
                    "resources": len(resources),
                    "tool_names": [t.name for t in tools],
                    "resource_uris": [r.uri for r in resources]
                }
        except Exception:
            return None
    
    try:
        return asyncio.run(_get_info())
    except Exception:
        return None