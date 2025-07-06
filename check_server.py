#!/usr/bin/env python3

import subprocess
import sys
import time

# Just run the server and see what it outputs
cmd = ["python", "my_tools_server.py"]

print("Starting server process...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Give it a moment to start
time.sleep(2)

print("Checking if server is running...")
poll_result = proc.poll()
if poll_result is None:
    print("Server is running")
else:
    print(f"Server exited with code: {poll_result}")

# Try to get any output
try:
    stdout_data, stderr_data = proc.communicate(timeout=3)
    print(f"Stdout: {stdout_data}")
    print(f"Stderr: {stderr_data}")
except subprocess.TimeoutExpired:
    print("Server is still running after 3 seconds")
    proc.terminate()
    stdout_data, stderr_data = proc.communicate()
    print(f"Stdout: {stdout_data}")
    print(f"Stderr: {stderr_data}")