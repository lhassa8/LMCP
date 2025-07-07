#!/usr/bin/env python3
"""
Simple MCP Client - Actually Works!

A dead simple way to discover and use MCP servers without complex protocols.
"""

import asyncio
import json
import subprocess
import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import platform

@dataclass
class Server:
    name: str
    description: str
    install_cmd: str
    run_cmd: str
    verified: bool = False

class SimpleMCP:
    """Dead simple MCP client that actually works."""
    
    def __init__(self):
        self.servers = {
            # Verified working servers
            "filesystem": Server(
                name="filesystem",
                description="File operations (read, write, list files)",
                install_cmd="npm install -g @modelcontextprotocol/server-filesystem",
                run_cmd="npx @modelcontextprotocol/server-filesystem .",
                verified=True
            ),
            
            # Popular community servers 
            "desktop-commander": Server(
                name="desktop-commander", 
                description="Terminal operations and file editing",
                install_cmd="npm install -g @wonderwhy-er/desktop-commander",
                run_cmd="npx @wonderwhy-er/desktop-commander",
                verified=False
            ),
            "gmail": Server(
                name="gmail",
                description="Gmail operations with auto authentication", 
                install_cmd="npm install -g @gongrzhe/server-gmail-autoauth-mcp",
                run_cmd="npx @gongrzhe/server-gmail-autoauth-mcp",
                verified=False
            ),
            "figma": Server(
                name="figma",
                description="Figma design operations",
                install_cmd="npm install -g figma-mcp",
                run_cmd="npx figma-mcp",
                verified=False
            ),
            "jsonresume": Server(
                name="jsonresume", 
                description="JSON Resume operations",
                install_cmd="npm install -g jsonresume-mcp",
                run_cmd="npx jsonresume-mcp",
                verified=False
            ),
            "filesystem-secure": Server(
                name="filesystem-secure",
                description="Secure filesystem with relative path support",
                install_cmd="npm install -g @m_sea_bass/relpath-filesystem-mcp", 
                run_cmd="npx @m_sea_bass/relpath-filesystem-mcp",
                verified=False
            ),
            "filesystem-advanced": Server(
                name="filesystem-advanced",
                description="Advanced file operations with search and replace",
                install_cmd="npm install -g @cyanheads/filesystem-mcp-server",
                run_cmd="npx @cyanheads/filesystem-mcp-server",
                verified=False
            ),
            "supergateway": Server(
                name="supergateway",
                description="Run MCP stdio servers over SSE/HTTP",
                install_cmd="npm install -g supergateway", 
                run_cmd="npx supergateway",
                verified=False
            ),
            
            # No-credential utility servers
            "hello-world": Server(
                name="hello-world",
                description="Simple Hello World MCP server for testing",
                install_cmd="npm install -g mcp-hello-world",
                run_cmd="npx mcp-hello-world",
                verified=True
            ),
            "calculator": Server(
                name="calculator",
                description="Calculator for precise numerical calculations",
                install_cmd="npm install -g @wrtnlabs/calculator-mcp",
                run_cmd="npx @wrtnlabs/calculator-mcp",
                verified=False
            ),
            "dad-jokes": Server(
                name="dad-jokes",
                description="The one and only MCP Server for dad jokes",
                install_cmd="npm install -g model-context-protocol",
                run_cmd="npx model-context-protocol",
                verified=False
            ),
            "sequential-thinking": Server(
                name="sequential-thinking",
                description="Sequential thinking and problem solving tools",
                install_cmd="npm install -g @modelcontextprotocol/server-sequential-thinking",
                run_cmd="npx @modelcontextprotocol/server-sequential-thinking",
                verified=True
            ),
            "wikipedia": Server(
                name="wikipedia",
                description="Wikipedia API interactions and search",
                install_cmd="npm install -g @shelm/wikipedia-mcp-server",
                run_cmd="npx @shelm/wikipedia-mcp-server",
                verified=True
            ),
            "code-runner": Server(
                name="code-runner",
                description="Code execution and running capabilities",
                install_cmd="npm install -g mcp-server-code-runner",
                run_cmd="npx mcp-server-code-runner",
                verified=False
            ),
            "kubernetes": Server(
                name="kubernetes",
                description="Kubernetes cluster interactions via kubectl",
                install_cmd="npm install -g mcp-server-kubernetes",
                run_cmd="npx mcp-server-kubernetes",
                verified=False
            ),
            "elasticsearch": Server(
                name="elasticsearch",
                description="Elasticsearch search and indexing operations",
                install_cmd="npm install -g @elastic/mcp-server-elasticsearch",
                run_cmd="npx @elastic/mcp-server-elasticsearch",
                verified=False
            ),
            "basic-mcp": Server(
                name="basic-mcp",
                description="Basic MCP server implementation",
                install_cmd="npm install -g mcp-server",
                run_cmd="npx mcp-server",
                verified=False
            ),
            "mysql": Server(
                name="mysql",
                description="MySQL database interactions",
                install_cmd="npm install -g @benborla29/mcp-server-mysql",
                run_cmd="npx @benborla29/mcp-server-mysql",
                verified=False
            )
        }
    
    def list_servers(self):
        """List available servers."""
        print("🌐 Available MCP Servers:")
        print("=" * 50)
        for name, server in self.servers.items():
            status = "✅" if server.verified else "⚠️"
            print(f"{status} {name:15} - {server.description}")
        print()
    
    def install_server(self, name: str) -> bool:
        """Install a server using npm."""
        if name not in self.servers:
            print(f"❌ Server '{name}' not found")
            return False
        
        server = self.servers[name]
        print(f"📦 Installing {name}...")
        print(f"Command: {server.install_cmd}")
        
        try:
            # Run npm install
            result = subprocess.run(
                server.install_cmd.split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ {name} installed successfully!")
                if result.stdout:
                    print("Output:", result.stdout.strip())
                return True
            else:
                print(f"❌ Installation failed")
                print("Error:", result.stderr.strip())
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    async def test_server(self, name: str) -> bool:
        """Test if a server works by sending a simple request."""
        if name not in self.servers:
            print(f"❌ Server '{name}' not found")
            return False
        
        server = self.servers[name]
        print(f"🧪 Testing {name}...")
        
        try:
            # Start the server process
            if platform.system() == "Windows":
                # Windows needs shell=True
                cmd = server.run_cmd
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE, 
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                # Unix-like systems
                cmd_parts = server.run_cmd.split()
                process = await asyncio.create_subprocess_exec(
                    *cmd_parts,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize", 
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "simple-mcp", "version": "1.0"}
                }
            }
            
            # Send the request
            request_json = json.dumps(init_request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    process.stdout.readline(), 
                    timeout=5.0
                )
                response = json.loads(response_line.decode().strip())
                
                if "result" in response:
                    print(f"✅ {name} is working!")
                    
                    # Try to list tools
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2, 
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    tools_json = json.dumps(tools_request) + "\n"
                    process.stdin.write(tools_json.encode())
                    await process.stdin.drain()
                    
                    tools_response_line = await asyncio.wait_for(
                        process.stdout.readline(),
                        timeout=5.0
                    )
                    tools_response = json.loads(tools_response_line.decode().strip())
                    
                    if "result" in tools_response and "tools" in tools_response["result"]:
                        tools = tools_response["result"]["tools"]
                        print(f"🔧 Found {len(tools)} tools: {', '.join([t['name'] for t in tools[:3]])}")
                        if len(tools) > 3:
                            print(f"   ... and {len(tools) - 3} more")
                    
                    return True
                else:
                    print(f"❌ Server error: {response.get('error', 'Unknown')}")
                    return False
                    
            except asyncio.TimeoutError:
                print(f"❌ {name} timed out")
                return False
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                return False
                
        except FileNotFoundError:
            print(f"❌ Command not found. Try installing first:")
            print(f"   {server.install_cmd}")
            return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            # Clean up process
            try:
                if 'process' in locals() and process and process.returncode is None:
                    # Close stdin first to signal the process to exit gracefully
                    if process.stdin and not process.stdin.is_closing():
                        process.stdin.close()
                    
                    # Wait a moment for graceful shutdown
                    try:
                        await asyncio.wait_for(process.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        # Force terminate if graceful shutdown failed
                        process.terminate()
                        try:
                            await asyncio.wait_for(process.wait(), timeout=1.0)
                        except asyncio.TimeoutError:
                            # Force kill if terminate failed
                            process.kill()
                            await process.wait()
            except Exception:
                # Ignore cleanup errors to prevent masking the original error
                pass
    
    async def get_tool_schema(self, server_name: str, tool_name: str) -> dict:
        """Get the schema for a specific tool."""
        inspection_result = await self.inspect_server(server_name)
        
        if "error" in inspection_result:
            return inspection_result
        
        if "result" in inspection_result and "tools" in inspection_result["result"]:
            for tool in inspection_result["result"]["tools"]:
                if tool["name"] == tool_name:
                    return {"tool": tool}
        
        return {"error": f"Tool '{tool_name}' not found in server '{server_name}'"}
    
    async def call_tool(self, server_name: str, tool_name: str, **params) -> dict:
        """Call a tool on a server."""
        if server_name not in self.servers:
            return {"error": f"Server '{server_name}' not found"}
        
        server = self.servers[server_name]
        print(f"🔧 Calling {tool_name} on {server_name}...")
        
        try:
            # Start server
            if platform.system() == "Windows":
                process = await asyncio.create_subprocess_shell(
                    server.run_cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                cmd_parts = server.run_cmd.split()
                process = await asyncio.create_subprocess_exec(
                    *cmd_parts,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE, 
                    stderr=asyncio.subprocess.PIPE
                )
            
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05", 
                    "capabilities": {},
                    "clientInfo": {"name": "simple-mcp", "version": "1.0"}
                }
            }
            
            process.stdin.write((json.dumps(init_request) + "\n").encode())
            await process.stdin.drain()
            
            # Read init response
            await process.stdout.readline()  # Skip init response
            
            # Call tool
            tool_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                }
            }
            
            process.stdin.write((json.dumps(tool_request) + "\n").encode())
            await process.stdin.drain()
            
            # Read tool response
            response_line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=10.0
            )
            response = json.loads(response_line.decode().strip())
            
            return response
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            try:
                if 'process' in locals() and process and process.returncode is None:
                    # Close stdin first to signal the process to exit gracefully
                    if process.stdin and not process.stdin.is_closing():
                        process.stdin.close()
                    
                    # Wait a moment for graceful shutdown
                    try:
                        await asyncio.wait_for(process.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        # Force terminate if graceful shutdown failed
                        process.terminate()
                        try:
                            await asyncio.wait_for(process.wait(), timeout=1.0)
                        except asyncio.TimeoutError:
                            # Force kill if terminate failed
                            process.kill()
                            await process.wait()
            except Exception:
                # Ignore cleanup errors to prevent masking the original error
                pass
    
    async def inspect_server(self, server_name: str) -> dict:
        """Inspect a server to discover its tools and their schemas."""
        if server_name not in self.servers:
            return {"error": f"Server '{server_name}' not found"}
        
        server = self.servers[server_name]
        print(f"🔍 Inspecting {server_name}...")
        
        try:
            # Start server
            if platform.system() == "Windows":
                process = await asyncio.create_subprocess_shell(
                    server.run_cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                cmd_parts = server.run_cmd.split()
                process = await asyncio.create_subprocess_exec(
                    *cmd_parts,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "simple-mcp", "version": "1.0"}
                }
            }
            
            process.stdin.write((json.dumps(init_request) + "\n").encode())
            await process.stdin.drain()
            
            # Read init response
            await process.stdout.readline()
            
            # List tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            process.stdin.write((json.dumps(tools_request) + "\n").encode())
            await process.stdin.drain()
            
            # Read tools response
            tools_response_line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=10.0
            )
            tools_response = json.loads(tools_response_line.decode().strip())
            
            return tools_response
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            try:
                if 'process' in locals() and process and process.returncode is None:
                    # Close stdin first to signal the process to exit gracefully
                    if process.stdin and not process.stdin.is_closing():
                        process.stdin.close()
                    
                    # Wait a moment for graceful shutdown
                    try:
                        await asyncio.wait_for(process.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        # Force terminate if graceful shutdown failed
                        process.terminate()
                        try:
                            await asyncio.wait_for(process.wait(), timeout=1.0)
                        except asyncio.TimeoutError:
                            # Force kill if terminate failed
                            process.kill()
                            await process.wait()
            except Exception:
                # Ignore cleanup errors to prevent masking the original error
                pass