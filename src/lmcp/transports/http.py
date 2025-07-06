"""
HTTP Transport Implementation

Provides communication over HTTP/HTTPS with Server-Sent Events.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, AsyncIterator
from urllib.parse import urlparse

import httpx

from .base import Transport
from ..exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class HttpTransport(Transport):
    """Transport implementation using HTTP with Server-Sent Events."""
    
    def __init__(self, config):
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None
        self._base_url: Optional[str] = None
        self._session_id: Optional[str] = None
        self._event_stream: Optional[AsyncIterator[str]] = None
    
    async def connect(self, uri: str) -> None:
        """Connect to an HTTP MCP server."""
        if self._connected:
            return
        
        try:
            parsed = urlparse(uri)
            if parsed.scheme not in ("http", "https"):
                raise ConnectionError(f"Invalid HTTP URI: {uri}")
            
            self._base_url = f"{parsed.scheme}://{parsed.netloc}"
            if parsed.path:
                self._base_url += parsed.path
            
            # Create HTTP client
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=self.config.headers
            )
            
            # Initialize session
            await self._initialize_session()
            
            # Start event stream
            await self._start_event_stream()
            
            self._connected = True
            logger.info(f"Connected to HTTP MCP server: {self._base_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect via HTTP: {e}")
            if self._client:
                await self._client.aclose()
                self._client = None
            raise ConnectionError(f"Failed to connect via HTTP: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the HTTP server."""
        if not self._connected:
            return
        
        try:
            # Close event stream
            if self._event_stream:
                await self._event_stream.aclose()
                self._event_stream = None
            
            # Close session
            if self._session_id and self._client:
                try:
                    await self._client.delete(f"{self._base_url}/session/{self._session_id}")
                except Exception as e:
                    logger.warning(f"Failed to close session: {e}")
            
            # Close HTTP client
            if self._client:
                await self._client.aclose()
                self._client = None
            
            self._connected = False
            logger.info("Disconnected from HTTP MCP server")
            
        except Exception as e:
            logger.error(f"Error during HTTP disconnect: {e}")
            raise ConnectionError(f"Failed to disconnect: {e}")
    
    async def _initialize_session(self) -> None:
        """Initialize a new session with the server."""
        if not self._client:
            raise ConnectionError("HTTP client not initialized")
        
        try:
            response = await self._client.post(
                f"{self._base_url}/session",
                json={"client_info": {"name": "lmcp", "version": "0.1.0"}}
            )
            response.raise_for_status()
            
            session_data = response.json()
            self._session_id = session_data.get("session_id")
            
            if not self._session_id:
                raise ConnectionError("Server did not return session ID")
            
            logger.debug(f"Session initialized: {self._session_id}")
            
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"HTTP error during session init: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize session: {e}")
    
    async def _start_event_stream(self) -> None:
        """Start the Server-Sent Events stream."""
        if not self._client or not self._session_id:
            raise ConnectionError("Session not initialized")
        
        try:
            # Start SSE stream
            stream_url = f"{self._base_url}/session/{self._session_id}/events"
            
            async with self._client.stream("GET", stream_url) as response:
                response.raise_for_status()
                self._event_stream = response.aiter_text()
                
            logger.debug("Event stream started")
            
        except Exception as e:
            raise ConnectionError(f"Failed to start event stream: {e}")
    
    async def send(self, data: Dict[str, Any]) -> None:
        """Send data to the server via HTTP POST."""
        if not self._connected or not self._client or not self._session_id:
            raise ConnectionError("Not connected")
        
        try:
            response = await self._client.post(
                f"{self._base_url}/session/{self._session_id}/messages",
                json=data
            )
            response.raise_for_status()
            
            logger.debug(f"Sent HTTP message: {data}")
            
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"HTTP error during send: {e}")
        except Exception as e:
            logger.error(f"Failed to send HTTP data: {e}")
            raise ConnectionError(f"Send failed: {e}")
    
    async def receive(self) -> Dict[str, Any]:
        """Receive data from the server via SSE."""
        if not self._connected or not self._event_stream:
            raise ConnectionError("Not connected")
        
        try:
            # Read from event stream
            async for chunk in self._event_stream:
                if chunk.strip():
                    # Parse SSE format
                    if chunk.startswith("data: "):
                        data_str = chunk[6:].strip()
                        if data_str and data_str != "[DONE]":
                            data = json.loads(data_str)
                            logger.debug(f"Received HTTP message: {data}")
                            return data
            
            raise ConnectionError("Event stream closed")
            
        except json.JSONDecodeError as e:
            raise ConnectionError(f"Invalid JSON in SSE: {e}")
        except Exception as e:
            logger.error(f"Failed to receive HTTP data: {e}")
            raise ConnectionError(f"Receive failed: {e}")
    
    async def ping(self) -> None:
        """Send a ping to test connectivity."""
        if not self._connected or not self._client or not self._session_id:
            raise ConnectionError("Not connected")
        
        try:
            response = await self._client.get(
                f"{self._base_url}/session/{self._session_id}/ping"
            )
            response.raise_for_status()
            
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"HTTP ping failed: {e}")
        except Exception as e:
            raise ConnectionError(f"Ping failed: {e}")