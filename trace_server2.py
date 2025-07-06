#!/usr/bin/env python3

import asyncio
import my_tools_server
import lmcp

async def trace_server():
    print("1. Creating server...")
    server = my_tools_server.MytoolsServer()
    print(f"   Server created: {server}")
    print(f"   Server class: {server.__class__}")
    print(f"   Server attributes: {[attr for attr in dir(server) if not attr.startswith('__')]}")
    
    print("2. Starting server...")
    try:
        await server.start()
        print("   Server start() completed")
        
        print("3. Checking server state...")
        print(f"   Running: {getattr(server, '_running', 'not found')}")
        print(f"   MCP Server: {getattr(server, '_mcp_server', 'not found')}")
        
        if hasattr(server, '_mcp_server') and server._mcp_server:
            print(f"   MCP Server initialized: {getattr(server._mcp_server, '_initialized', 'not found')}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trace_server())