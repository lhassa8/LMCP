#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Test the actual LMCP server with debug logging
cmd = ["python", "-c", """
import logging
logging.basicConfig(level=logging.DEBUG, format='SERVER: %(levelname)s - %(message)s')

import my_tools_server
import lmcp

server = my_tools_server.MytoolsServer()
lmcp.run_server(server)
"""]

print("Starting LMCP server with debug logging...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Wait for startup
time.sleep(2)

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

print(f"Sending: {json.dumps(init_request)}")
proc.stdin.write(json.dumps(init_request) + "\n")
proc.stdin.flush()

# Wait a bit and check output
time.sleep(3)

# Check stdout
try:
    # Non-blocking read
    import fcntl
    import os
    
    # Make stdout non-blocking
    fd = proc.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    try:
        stdout_data = proc.stdout.read()
        if stdout_data:
            print(f"Stdout: {stdout_data}")
    except BlockingIOError:
        print("No stdout data")
    
    # Make stderr non-blocking
    fd = proc.stderr.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    try:
        stderr_data = proc.stderr.read()
        if stderr_data:
            print(f"Stderr: {stderr_data}")
    except BlockingIOError:
        print("No stderr data")
        
except Exception as e:
    print(f"Error reading output: {e}")

# Clean up
proc.terminate()
proc.wait()