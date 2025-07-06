#!/usr/bin/env python3
"""
Proper stdio-based MCP server implementation

This server properly handles MCP protocol over stdio by:
1. Reading JSON-RPC messages from stdin line by line
2. Processing them according to MCP protocol
3. Writing responses to stdout
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

# Configure logging to stderr so it doesn't interfere with stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

class StdioMCPServer:
    """MCP server that handles stdio-based communication"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.initialized = False
        self.client_info = None
        self.capabilities = {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True}
        }
        
        # Register tools
        self.tools = {
            "add": {
                "description": "Add two numbers together",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            },
            "sqrt": {
                "description": "Calculate the square root of a number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"}
                    },
                    "required": ["x"]
                }
            },
            "greet": {
                "description": "Generate a friendly greeting",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": []
                }
            }
        }
    
    async def handle_message(self, message: str) -> Optional[str]:
        """Handle an incoming message and return response"""
        try:
            data = json.loads(message)
            logger.debug(f"Received message: {data}")
            
            # Check if it's a request (has method and id)
            if "method" in data and "id" in data:
                response = await self.handle_request(data)
                if response:
                    return json.dumps(response)
            
            # Check if it's a notification (has method but no id)
            elif "method" in data and "id" not in data:
                await self.handle_notification(data)
                return None
            
            else:
                logger.warning(f"Unknown message format: {data}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return None
    
    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle a request and return response"""
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})
        
        logger.debug(f"Handling request: {method}")
        
        if method == "initialize":
            return await self.handle_initialize(request_id, params)
        elif method == "tools/list":
            return await self.handle_list_tools(request_id, params)
        elif method == "tools/call":
            return await self.handle_call_tool(request_id, params)
        elif method == "ping":
            return await self.handle_ping(request_id, params)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def handle_notification(self, notification: Dict[str, Any]) -> None:
        """Handle a notification"""
        method = notification.get("method")
        params = notification.get("params", {})
        
        logger.debug(f"Handling notification: {method}")
        
        if method == "notifications/initialized":
            self.initialized = True
            logger.info("Client has initialized")
        elif method == "notifications/cancelled":
            logger.info("Request cancelled")
        else:
            logger.debug(f"Unknown notification: {method}")
    
    async def handle_initialize(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        self.client_info = params.get("clientInfo", {})
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                    "description": f"Sample MCP server: {self.name}"
                },
                "capabilities": self.capabilities
            }
        }
    
    async def handle_list_tools(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list tools request"""
        tools = []
        for name, info in self.tools.items():
            tools.append({
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            })
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def handle_call_tool(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle call tool request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        try:
            result = await self.execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def handle_ping(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "type": "pong"
            }
        }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        if tool_name == "add":
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            return a + b
        elif tool_name == "sqrt":
            import math
            x = arguments.get("x", 0)
            if x < 0:
                raise ValueError("Cannot calculate square root of negative number")
            return math.sqrt(x)
        elif tool_name == "greet":
            name = arguments.get("name", "World")
            return f"Hello, {name}! 👋"
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def run(self):
        """Run the server, reading from stdin and writing to stdout"""
        logger.info(f"Starting MCP server: {self.name}")
        
        # Read from stdin line by line
        while True:
            try:
                # Read a line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    # EOF reached
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Process the message
                response = await self.handle_message(line)
                
                if response:
                    # Write response to stdout
                    print(response, flush=True)
                
            except KeyboardInterrupt:
                logger.info("Server interrupted")
                break
            except Exception as e:
                logger.error(f"Error in server loop: {e}")
                break
        
        logger.info("Server stopped")

async def main():
    """Main function"""
    server = StdioMCPServer("my-tools")
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())