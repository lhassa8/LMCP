#!/usr/bin/env python3
"""Test to reproduce the CLI timeout issue"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lmcp.client import Client
from lmcp.types import ConnectionConfig

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_cli_issue():
    """Test to reproduce the CLI issue"""
    
    try:
        print("=== Testing CLI Issue ===")
        
        # This should reproduce the exact same issue as the CLI
        config = ConnectionConfig(uri="stdio://python stdio_mcp_server.py", timeout=10.0)
        client = Client("stdio://python stdio_mcp_server.py", config)
        
        print("1. Attempting to connect...")
        await client.connect()  # This should hang due to the deadlock
        
        print("2. Connected successfully!")
        print(f"Server info: {client.server_info}")
        
        print("3. Listing tools...")
        tools = await client.list_tools()
        print(f"Tools: {[tool.name for tool in tools]}")
        
        await client.disconnect()
        print("4. Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cli_issue())