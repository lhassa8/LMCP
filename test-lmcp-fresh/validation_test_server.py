"""
Validation-Test MCP Server

A sample MCP server created with LMCP.
"""

import lmcp
import math

@lmcp.server("validation-test")
class ValidationtestServer:
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
        return f"Hello, {name}! 👋"
    
    @lmcp.resource("server://info", description="Server information")
    def server_info(self) -> dict:
        """Get information about this server."""
        return {
            "name": "validation-test",
            "version": "1.0.0",
            "capabilities": ["math", "greetings"],
            "status": "running"
        }
    
    @lmcp.resource("server://stats", description="Server statistics")
    def server_stats(self) -> dict:
        """Get server statistics."""
        return {
            "tools": len(self.list_tools()),
            "resources": len(self.list_resources()),
            "uptime": "just started"
        }

if __name__ == "__main__":
    import sys
    
    # Only show startup messages if not in stdio mode
    if sys.stdout.isatty():
        print("🚀 Starting validation-test server...")
        print("📋 Available tools: add, sqrt, greet")
        print("📁 Available resources: server://info, server://stats")
        print("🌐 Use the LMCP CLI to test: lmcp client list-tools stdio://python validation_test_server.py")
        print()
    
    server = ValidationtestServer()
    lmcp.run_server(server)
