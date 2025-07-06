"""
Basic LMCP Client Example

Demonstrates how to use the LMCP client to connect to an MCP server.
"""

import asyncio
import logging
from lmcp import connect, ConnectionConfig


async def main():
    """Basic client example."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Connect to a filesystem server
    print("🔌 Connecting to filesystem server...")
    
    async with connect("stdio://mcp-server-filesystem") as client:
        # Check connection
        print(f"✅ Connected to: {client.server_info.name}")
        print(f"📝 Description: {client.server_info.description}")
        
        # List available tools
        print("\n🔧 Available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # List available resources
        print("\n📁 Available resources:")
        resources = await client.list_resources()
        for resource in resources:
            print(f"  - {resource.uri}: {resource.description}")
        
        # Call a tool (example)
        try:
            print("\n🛠️ Calling list_files tool...")
            result = await client.tools.list_files(path=".")
            if result.is_error:
                print(f"❌ Error: {result.error_message}")
            else:
                print(f"📋 Result: {result.content}")
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
        
        # Get a resource (example)
        try:
            print("\n📄 Getting README.md resource...")
            result = await client.resources.get("file://README.md")
            print(f"📋 Content preview: {str(result.content)[:200]}...")
        except Exception as e:
            print(f"❌ Resource fetch failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())