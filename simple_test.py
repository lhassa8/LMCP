#!/usr/bin/env python3

import sys
import json

# Simple test: just echo what we receive
while True:
    try:
        line = input()
        if not line.strip():
            continue
        
        # Try to parse as JSON
        try:
            msg = json.loads(line)
            print(f"Received: {msg}")
            
            # Send back a simple response
            response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": "OK"}
            print(json.dumps(response))
            
        except json.JSONDecodeError:
            print(f"Invalid JSON: {line}")
            
    except EOFError:
        break
    except KeyboardInterrupt:
        break