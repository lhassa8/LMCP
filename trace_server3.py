#!/usr/bin/env python3

import asyncio
import my_tools_server
import lmcp

async def trace_server():
    print("1. Creating server...")
    server = my_tools_server.MytoolsServer()
    
    print("2. Starting server...")
    await server.start()
    
    print("3. Checking MCP server state...")
    mcp_server = server._mcp_server
    print(f"   MCP Server: {mcp_server}")
    print(f"   MCP Server initialized: {mcp_server._initialized}")
    print(f"   MCP Server transport: {mcp_server.config.transport}")
    
    # Check if stdin task exists
    stdin_task = getattr(mcp_server, '_stdin_task', None)
    print(f"   Stdin task: {stdin_task}")
    
    if stdin_task:
        print(f"   Stdin task done: {stdin_task.done()}")
        if stdin_task.done():
            try:
                stdin_task.result()
                print("   Stdin task completed successfully")
            except Exception as e:
                print(f"   Stdin task failed: {e}")
    
    print("4. Sending a test message to server...")
    # Try to send a message directly to the server
    test_message = {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test", "version": "1.0.0"},
            "capabilities": {}
        }
    }
    
    response = await mcp_server.handle_message(test_message)
    print(f"   Response: {response}")

if __name__ == "__main__":
    asyncio.run(trace_server())