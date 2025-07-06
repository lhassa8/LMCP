#!/usr/bin/env python3
"""Debug the stdio transport to see what's happening"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lmcp.transports.stdio import StdioTransport
from lmcp.types import ConnectionConfig

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def debug_stdio_transport():
    """Debug the stdio transport with the sample server"""
    
    # Create configuration
    config = ConnectionConfig(uri="stdio://python my_tools_server.py", timeout=10.0)
    transport = StdioTransport(config)
    
    try:
        print("=== Debugging STDIO Transport ===")
        
        # Test 1: Connection
        print("\n1. Testing connection...")
        await transport.connect("stdio://python my_tools_server.py")
        print("✓ Connection established")
        
        # Check if process is running
        if transport._process:
            print(f"Process PID: {transport._process.pid}")
            print(f"Process return code: {transport._process.returncode}")
            
            # Check stderr for any errors
            if transport._process.stderr:
                print("\n2. Checking stderr for errors...")
                try:
                    # Try to read from stderr (non-blocking)
                    stderr_data = await asyncio.wait_for(transport._process.stderr.read(1024), timeout=1.0)
                    if stderr_data:
                        print(f"STDERR: {stderr_data.decode('utf-8')}")
                    else:
                        print("No stderr data available")
                except asyncio.TimeoutError:
                    print("No stderr data available (timeout)")
        
        # Test 2: Send initialize request
        print("\n3. Sending initialize request...")
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
                "capabilities": {}
            }
        }
        
        await transport.send(init_request)
        print("✓ Initialize request sent")
        
        # Test 3: Wait for response with shorter timeout
        print("\n4. Waiting for initialize response...")
        try:
            response = await asyncio.wait_for(transport.receive(), timeout=3.0)
            print(f"✓ Received response: {json.dumps(response, indent=2)}")
        except asyncio.TimeoutError:
            print("✗ Timeout waiting for response")
            
            # Check if there's anything in stderr
            if transport._process and transport._process.stderr:
                try:
                    stderr_data = await asyncio.wait_for(transport._process.stderr.read(1024), timeout=1.0)
                    if stderr_data:
                        print(f"STDERR after timeout: {stderr_data.decode('utf-8')}")
                except asyncio.TimeoutError:
                    pass
        
        # Test 4: Check if the process is still alive
        print("\n5. Checking process status...")
        if transport._process:
            print(f"Process return code: {transport._process.returncode}")
            if transport._process.returncode is not None:
                print("Process has terminated!")
            else:
                print("Process is still running")
                
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n6. Disconnecting...")
        await transport.disconnect()
        print("✓ Disconnected")

if __name__ == "__main__":
    # Set environment
    import os
    os.environ["PYTHONPATH"] = "src"
    
    asyncio.run(debug_stdio_transport())