#!/usr/bin/env python3

import json
import subprocess
import sys

# Test the simple echo server
cmd = ["python", "simple_test.py"]

print("Starting simple echo server...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Send a test message
test_msg = {"jsonrpc": "2.0", "id": "test", "method": "test"}
msg_str = json.dumps(test_msg)

print(f"Sending: {msg_str}")
proc.stdin.write(msg_str + "\n")
proc.stdin.flush()

# Read response
try:
    response = proc.stdout.readline()
    print(f"Response: {response.strip()}")
    
    # Read actual response
    response2 = proc.stdout.readline()
    print(f"JSON Response: {response2.strip()}")
    
except Exception as e:
    print(f"Error: {e}")

# Clean up
proc.terminate()
proc.wait()