#!/usr/bin/env python3
"""
LMCP Get Started Script

The easiest way to try LMCP! Run this script to see it in action.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to path so we can import lmcp
sys.path.insert(0, str(Path(__file__).parent / "src"))

import lmcp


# Simple demo server
@lmcp.server("demo")
class DemoServer:
    """Demo server to show LMCP in action."""
    
    @lmcp.tool("Add two numbers")
    def add(self, a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b
    
    @lmcp.tool("Greet someone")
    def greet(self, name: str = "World") -> str:
        """Generate a friendly greeting."""
        return f"Hello, {name}! 👋 Welcome to LMCP!"
    
    @lmcp.tool("Calculate square")
    def square(self, x: int) -> int:
        """Calculate the square of a number."""
        return x * x
    
    @lmcp.resource("demo://info", description="Demo server info")
    def server_info(self) -> dict:
        """Get information about this demo server."""
        return {
            "name": "LMCP Demo Server",
            "version": "1.0.0",
            "description": "A simple demo showing LMCP capabilities",
            "tools": ["add", "greet", "square"],
            "message": "🎉 LMCP is working perfectly!"
        }


async def demo_client():
    """Demo the client connecting to our server."""
    print("🔌 Testing LMCP client connection...")
    
    # In a real scenario, you'd connect to a running server
    # For this demo, we'll show what the client code looks like
    print("""
📝 Here's how easy it is to use LMCP as a client:

```python
import lmcp

async def main():
    # Connect to any MCP server
    async with lmcp.connect("stdio://python my_server.py") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools!")
        
        # Call tools directly
        result = await client.tools.add(a=5, b=3)
        greeting = await client.tools.greet(name="LMCP User")
        
        print(f"5 + 3 = {result.content}")
        print(greeting.content)
```

That's it! Super simple! 🚀
""")


def main():
    """Main demo function."""
    print("🎉 Welcome to LMCP - Lightweight Model Context Protocol!")
    print("=" * 60)
    print()
    
    print("LMCP makes working with Claude's MCP super easy!")
    print("Let's see it in action...")
    print()
    
    # Show the server we created
    print("📋 Demo Server Created:")
    server = DemoServer()
    tools = server.list_tools()
    resources = server.list_resources()
    
    print(f"  Name: {server.name}")
    print(f"  Tools: {len(tools)}")
    for tool in tools:
        print(f"    - {tool.name}: {tool.description}")
    
    print(f"  Resources: {len(resources)}")
    for resource in resources:
        print(f"    - {resource.uri}: {resource.description}")
    print()
    
    # Show client demo
    asyncio.run(demo_client())
    
    print("🎯 What's Next?")
    print("=" * 20)
    print("1. Install LMCP: pip install lmcp")
    print("2. Create a server: lmcp create sample my-server")
    print("3. Run it: python my_server_server.py")
    print("4. Test it: lmcp client list-tools stdio://python my_server_server.py")
    print()
    print("📚 Check out the examples/ folder for more ideas!")
    print("🔗 Repository: https://github.com/lhassa8/LMCP")
    print()
    print("Happy coding! 🚀")


if __name__ == "__main__":
    main()