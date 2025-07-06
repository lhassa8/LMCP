#!/usr/bin/env python3

import asyncio
import json
import my_tools_server

async def debug_protocol():
    server = my_tools_server.MytoolsServer()
    
    print("Testing _list_tools_for_protocol:")
    tools = await server._list_tools_for_protocol()
    
    print(f"Number of tools: {len(tools)}")
    for tool in tools:
        print(f"Tool: {json.dumps(tool, indent=2)}")

if __name__ == "__main__":
    asyncio.run(debug_protocol())