#!/usr/bin/env python3

import my_tools_server

# Create server and check tools directly
server = my_tools_server.MytoolsServer()

print("Raw tools registry:")
for name, tool in server._tool_registry._tools.items():
    print(f"  {name}: {tool}")

print("\nTools from list_tools():")
tools = server.list_tools()
for tool in tools:
    print(f"  {tool}")
    print(f"    output_schema type: {type(tool.output_schema)}")
    print(f"    output_schema value: {tool.output_schema}")

print("\nTrying to model_dump():")
for tool in tools:
    try:
        dumped = tool.model_dump()
        print(f"  {tool.name}: {dumped}")
    except Exception as e:
        print(f"  {tool.name}: ERROR - {e}")