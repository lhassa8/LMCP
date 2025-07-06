#!/usr/bin/env python3

import asyncio
import my_tools_server
import lmcp

async def trace_server():
    print("1. Creating server...")
    server = my_tools_server.MytoolsServer()
    print(f"   Server created: {server}")
    print(f"   Transport: {server.config.transport}")
    
    print("2. Starting server...")
    try:
        await server.start()
        print("   Server started successfully")
        
        print("3. Checking server state...")
        print(f"   Initialized: {server._initialized}")
        print(f"   MCP Server: {server._mcp_server}")
        
        # Wait a bit
        print("4. Waiting 2 seconds...")
        await asyncio.sleep(2)
        
        print("5. Stopping server...")
        await server.stop()
        print("   Server stopped")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trace_server())