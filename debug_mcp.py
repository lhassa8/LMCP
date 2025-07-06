#!/usr/bin/env python3
"""
Debug MCP Protocol Communication

Test what messages are being sent to/from MCP servers
"""

import asyncio
import json
import subprocess
import sys

async def test_server_communication():
    """Test direct communication with an MCP server"""
    
    # Start the filesystem server
    process = await asyncio.create_subprocess_exec(
        "npx", "@modelcontextprotocol/server-filesystem", ".",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    print("🔍 Testing MCP Server Communication")
    print("="*50)
    
    try:
        # Test 1: Initialize
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "lmcp-debug",
                    "version": "0.1.0"
                }
            }
        }
        
        print("📤 Sending initialize request:")
        print(json.dumps(init_msg, indent=2))
        
        process.stdin.write((json.dumps(init_msg) + "\n").encode())
        await process.stdin.drain()
        
        # Read response
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        response = json.loads(response_line.decode().strip())
        print("📥 Initialize response:")
        print(json.dumps(response, indent=2))
        
        # Test 2: List tools with different method names
        for method in ["tools/list", "listTools", "list_tools"]:
            tools_msg = {
                "jsonrpc": "2.0", 
                "id": 2,
                "method": method,
                "params": {}
            }
            
            print(f"\n📤 Trying method '{method}':")
            print(json.dumps(tools_msg, indent=2))
            
            process.stdin.write((json.dumps(tools_msg) + "\n").encode())
            await process.stdin.drain()
            
            try:
                response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
                response = json.loads(response_line.decode().strip())
                print("📥 Response:")
                print(json.dumps(response, indent=2))
                
                if "result" in response and "tools" in response.get("result", {}):
                    print(f"✅ SUCCESS: Method '{method}' works!")
                    break
                elif "error" in response:
                    print(f"❌ Error with method '{method}': {response['error']}")
                    
            except asyncio.TimeoutError:
                print(f"⏰ Timeout with method '{method}'")
            except Exception as e:
                print(f"💥 Exception with method '{method}': {e}")
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
    
    finally:
        # Clean up
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            process.kill()

if __name__ == "__main__":
    asyncio.run(test_server_communication())