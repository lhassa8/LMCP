#!/usr/bin/env python3

import my_tools_server
import lmcp

# Create server and check configuration
server = my_tools_server.MytoolsServer()
print(f"Server config: {server.config}")
print(f"Server transport: {server.config.transport}")

# Check if it's configured correctly
if server.config.transport == "stdio":
    print("✅ Server is configured for stdio transport")
else:
    print(f"❌ Server is NOT configured for stdio transport, it's: {server.config.transport}")

# Check the server class
print(f"Server class: {server.__class__}")
print(f"Server name: {server.name}")