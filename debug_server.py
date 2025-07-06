#!/usr/bin/env python3

import asyncio
import logging
import my_tools_server
import lmcp

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def test_server():
    server = my_tools_server.MytoolsServer()
    print(f"Server created: {server}")
    print(f"Server name: {server.name}")
    print(f"Tools: {server.list_tools()}")
    
    # Try to start the server
    try:
        await server.start()
        print("Server started successfully")
        await asyncio.sleep(2)
        await server.stop()
        print("Server stopped successfully")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server())