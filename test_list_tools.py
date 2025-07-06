#!/usr/bin/env python3

import json
import subprocess
import time

# Test the actual LMCP server with tools/list request
cmd = ["python", "my_tools_server.py"]

print("Starting LMCP server...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Wait for startup
time.sleep(1)

# Send initialize request first
init_request = {
    "jsonrpc": "2.0",
    "id": "1", 
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
        "capabilities": {}
    }
}

print("Sending initialize...")
proc.stdin.write(json.dumps(init_request) + "\n")
proc.stdin.flush()

# Read initialize response
init_response = proc.stdout.readline()
print(f"Init response: {init_response.strip()}")

# Send initialized notification
init_notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}

print("Sending initialized notification...")
proc.stdin.write(json.dumps(init_notification) + "\n")
proc.stdin.flush()

# Send tools/list request
tools_request = {
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/list",
    "params": {}
}

print("Sending tools/list...")
proc.stdin.write(json.dumps(tools_request) + "\n")
proc.stdin.flush()

# Read tools response
tools_response = proc.stdout.readline()
print(f"Tools response: {tools_response.strip()}")

# Clean up
proc.terminate()
proc.wait()