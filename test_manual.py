#!/usr/bin/env python3

import json
import subprocess
import sys

# Test the server manually
cmd = ["python", "my_tools_server.py"]

print("Starting server process...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Send initialize request
init_request = {
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
        "capabilities": {}
    }
}

print("Sending initialize request:")
print(json.dumps(init_request))

# Send the request
proc.stdin.write(json.dumps(init_request) + "\n")
proc.stdin.flush()

# Read response
print("\nWaiting for response...")
try:
    response = proc.stdout.readline()
    if response:
        print(f"Response: {response.strip()}")
    else:
        print("No response received")
    
    # Check stderr
    stderr_output = proc.stderr.readline()
    if stderr_output:
        print(f"Stderr: {stderr_output.strip()}")
        
except Exception as e:
    print(f"Error: {e}")

# Clean up
proc.terminate()
proc.wait()