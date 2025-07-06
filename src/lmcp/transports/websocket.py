"""
WebSocket Transport Implementation

Provides communication over WebSocket connections.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from .base import Transport
from ..exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class WebSocketTransport(Transport):
    """Transport implementation using WebSocket."""
    
    def __init__(self, config):
        super().__init__(config)
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._uri: Optional[str] = None
    
    async def connect(self, uri: str) -> None:
        """Connect to a WebSocket MCP server."""
        if self._connected:
            return
        
        try:
            parsed = urlparse(uri)
            if parsed.scheme not in ("ws", "wss"):
                raise ConnectionError(f"Invalid WebSocket URI: {uri}")
            
            self._uri = uri
            
            # Connect to WebSocket
            extra_headers = self.config.headers if self.config.headers else None
            
            self._websocket = await asyncio.wait_for(
                websockets.connect(
                    uri,
                    extra_headers=extra_headers,
                    ping_interval=20,  # Send ping every 20 seconds
                    ping_timeout=10,   # Wait 10 seconds for pong
                    close_timeout=10,  # Wait 10 seconds for close
                ),
                timeout=self.config.timeout
            )
            
            self._connected = True
            logger.info(f"Connected to WebSocket MCP server: {uri}")
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"WebSocket connection timeout after {self.config.timeout} seconds")
        except Exception as e:
            logger.error(f"Failed to connect via WebSocket: {e}")
            raise ConnectionError(f"Failed to connect via WebSocket: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        if not self._connected:
            return
        
        try:
            if self._websocket:
                await self._websocket.close()
                self._websocket = None
            
            self._connected = False
            logger.info("Disconnected from WebSocket MCP server")
            
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {e}")
            raise ConnectionError(f"Failed to disconnect: {e}")
    
    async def send(self, data: Dict[str, Any]) -> None:
        """Send JSON data via WebSocket."""
        if not self._connected or not self._websocket:
            raise ConnectionError("Not connected")
        
        try:
            # Serialize to JSON
            json_data = json.dumps(data)
            
            # Send via WebSocket
            await asyncio.wait_for(
                self._websocket.send(json_data),
                timeout=self.config.timeout
            )
            
            logger.debug(f"Sent WebSocket message: {json_data}")
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"WebSocket send timeout after {self.config.timeout} seconds")
        except ConnectionClosed:
            self._connected = False
            raise ConnectionError("WebSocket connection closed")
        except WebSocketException as e:
            raise ConnectionError(f"WebSocket error during send: {e}")
        except Exception as e:
            logger.error(f"Failed to send WebSocket data: {e}")
            raise ConnectionError(f"Send failed: {e}")
    
    async def receive(self) -> Dict[str, Any]:
        """Receive JSON data via WebSocket."""
        if not self._connected or not self._websocket:
            raise ConnectionError("Not connected")
        
        try:
            # Receive from WebSocket
            message = await asyncio.wait_for(
                self._websocket.recv(),
                timeout=self.config.timeout
            )
            
            # Parse JSON
            data = json.loads(message)
            
            logger.debug(f"Received WebSocket message: {message}")
            return data
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"WebSocket receive timeout after {self.config.timeout} seconds")
        except ConnectionClosed:
            self._connected = False
            raise ConnectionError("WebSocket connection closed")
        except json.JSONDecodeError as e:
            raise ConnectionError(f"Invalid JSON received: {e}")
        except WebSocketException as e:
            raise ConnectionError(f"WebSocket error during receive: {e}")
        except Exception as e:
            logger.error(f"Failed to receive WebSocket data: {e}")
            raise ConnectionError(f"Receive failed: {e}")
    
    async def ping(self) -> None:
        """Send a ping to test connectivity."""
        if not self._connected or not self._websocket:
            raise ConnectionError("Not connected")
        
        try:
            # WebSocket has built-in ping/pong
            pong_waiter = await self._websocket.ping()
            await asyncio.wait_for(pong_waiter, timeout=10.0)
            
        except asyncio.TimeoutError:
            raise TimeoutError("WebSocket ping timeout")
        except ConnectionClosed:
            self._connected = False
            raise ConnectionError("WebSocket connection closed")
        except WebSocketException as e:
            raise ConnectionError(f"WebSocket ping failed: {e}")
        except Exception as e:
            raise ConnectionError(f"Ping failed: {e}")