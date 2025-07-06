#!/usr/bin/env python3
"""Test the proper stdio MCP server implementation"""

import sys
import asyncio
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lmcp.transports.stdio import StdioTransport
from lmcp.types import ConnectionConfig

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_proper_stdio():
    """Test the proper stdio MCP server"""
    
    # Create configuration
    config = ConnectionConfig(uri="stdio://python stdio_mcp_server.py", timeout=10.0)
    transport = StdioTransport(config)
    
    try:
        print("=== Testing Proper STDIO MCP Server ===")
        
        # Test 1: Connection
        print("\n1. Testing connection...")
        await transport.connect("stdio://python stdio_mcp_server.py")
        print("✓ Connection established")
        
        # Test 2: Send initialize request
        print("\n2. Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": "init-1",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "lmcp-test",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                }
            }
        }
        
        await transport.send(init_request)
        print("✓ Initialize request sent")
        
        # Test 3: Wait for response
        print("\n3. Waiting for initialize response...")
        response = await asyncio.wait_for(transport.receive(), timeout=5.0)
        print(f"✓ Received response: {json.dumps(response, indent=2)}")
        
        # Test 4: Send initialized notification
        print("\n4. Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await transport.send(initialized_notification)
        print("✓ Initialized notification sent")
        
        # Test 5: List tools
        print("\n5. Listing tools...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "list-tools-1"
        }
        await transport.send(list_tools_request)
        tools_response = await asyncio.wait_for(transport.receive(), timeout=5.0)
        print(f"✓ Tools response: {json.dumps(tools_response, indent=2)}")
        
        # Test 6: Call a tool
        print("\n6. Calling add tool...")
        call_tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": "call-tool-1",
            "params": {
                "name": "add",
                "arguments": {
                    "a": 5,
                    "b": 3
                }
            }
        }
        await transport.send(call_tool_request)
        tool_response = await asyncio.wait_for(transport.receive(), timeout=5.0)
        print(f"✓ Tool call response: {json.dumps(tool_response, indent=2)}")
        
        # Test 7: Test ping
        print("\n7. Testing ping...")
        ping_request = {
            "jsonrpc": "2.0",
            "method": "ping",
            "id": "ping-1"
        }
        await transport.send(ping_request)
        ping_response = await asyncio.wait_for(transport.receive(), timeout=5.0)
        print(f"✓ Ping response: {json.dumps(ping_response, indent=2)}")
        
        print("\n=== All tests completed successfully! ===")
        
    except asyncio.TimeoutError:
        print("✗ Test failed: Timeout waiting for response")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n8. Disconnecting...")
        await transport.disconnect()
        print("✓ Disconnected")

if __name__ == "__main__":
    asyncio.run(test_proper_stdio())