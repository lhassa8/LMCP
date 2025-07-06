#!/usr/bin/env python3

import json
import subprocess
import sys
import time

# Test the actual LMCP server
cmd = ["python", "my_tools_server.py"]

print("Starting LMCP server...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

# Wait a moment for startup
time.sleep(1)

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

# Try to read response with timeout
print("Waiting for response...")
try:
    # Read with a timeout
    import select
    import time
    
    start_time = time.time()
    timeout = 5  # 5 second timeout
    
    while time.time() - start_time < timeout:
        # Check if there's data to read
        ready, _, _ = select.select([proc.stdout], [], [], 0.1)
        
        if ready:
            response = proc.stdout.readline()
            if response:
                print(f"Response: {response.strip()}")
                break
        
        # Check if process is still running
        if proc.poll() is not None:
            print("Process has terminated")
            break
    else:
        print("Timeout - no response received")
    
    # Check stderr
    stderr_output = proc.stderr.read()
    if stderr_output:
        print(f"Stderr: {stderr_output}")
        
except Exception as e:
    print(f"Error: {e}")

# Clean up
proc.terminate()
proc.wait()