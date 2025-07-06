"""
LMCP Connection Management

Handles connection lifecycle and transport management.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse
from contextlib import asynccontextmanager

from .types import ConnectionConfig, HealthStatus
from .exceptions import ConnectionError, TimeoutError
from .transports import Transport, StdioTransport, HttpTransport, WebSocketTransport

logger = logging.getLogger(__name__)


class Connection:
    """Represents a connection to an MCP server."""
    
    def __init__(self, transport: Transport, config: ConnectionConfig):
        self.transport = transport
        self.config = config
        self._closed = False
        self._health_status = HealthStatus(
            status="healthy",
            last_check=datetime.now(),
            checks={}
        )
    
    async def send(self, data: Dict[str, Any]) -> None:
        """Send data through the connection."""
        if self._closed:
            raise ConnectionError("Connection is closed")
        
        try:
            await self.transport.send(data)
        except Exception as e:
            logger.error(f"Failed to send data: {e}")
            raise ConnectionError(f"Send failed: {e}")
    
    async def receive(self) -> Dict[str, Any]:
        """Receive data from the connection."""
        if self._closed:
            raise ConnectionError("Connection is closed")
        
        try:
            return await self.transport.receive()
        except Exception as e:
            logger.error(f"Failed to receive data: {e}")
            raise ConnectionError(f"Receive failed: {e}")
    
    async def close(self) -> None:
        """Close the connection."""
        if self._closed:
            return
        
        try:
            await self.transport.close()
            self._closed = True
            logger.debug("Connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed
    
    async def health_check(self) -> HealthStatus:
        """Check connection health."""
        if self._closed:
            return HealthStatus(
                status="unhealthy",
                last_check=datetime.now(),
                checks={"connection": "closed"}
            )
        
        try:
            # Simple health check - attempt to check transport
            health = await self.transport.health_check()
            self._health_status = health
            return health
        except Exception as e:
            self._health_status = HealthStatus(
                status="unhealthy",
                last_check=datetime.now(),
                checks={"error": str(e)}
            )
            return self._health_status


class ConnectionPool:
    """Pool of connections for reuse."""
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self._connections: Dict[str, Connection] = {}
        self._lock = asyncio.Lock()
    
    async def get_connection(self, uri: str, config: ConnectionConfig) -> Connection:
        """Get a connection from the pool or create a new one."""
        async with self._lock:
            # Check if we have an existing healthy connection
            if uri in self._connections:
                conn = self._connections[uri]
                if not conn.closed:
                    health = await conn.health_check()
                    if health.status == "healthy":
                        return conn
                    else:
                        # Remove unhealthy connection
                        await conn.close()
                        del self._connections[uri]
            
            # Create new connection
            if len(self._connections) >= self.max_size:
                # Remove oldest connection
                oldest_uri = next(iter(self._connections))
                await self._connections[oldest_uri].close()
                del self._connections[oldest_uri]
            
            # Create and store new connection
            conn = await self._create_connection(uri, config)
            self._connections[uri] = conn
            return conn
    
    async def _create_connection(self, uri: str, config: ConnectionConfig) -> Connection:
        """Create a new connection."""
        parsed = urlparse(uri)
        
        # Select transport based on scheme
        if parsed.scheme == "stdio":
            transport = StdioTransport(config)
        elif parsed.scheme in ("http", "https"):
            transport = HttpTransport(config)
        elif parsed.scheme in ("ws", "wss"):
            transport = WebSocketTransport(config)
        else:
            raise ConnectionError(f"Unsupported scheme: {parsed.scheme}")
        
        # Initialize transport
        await transport.connect(uri)
        
        return Connection(transport, config)
    
    async def close_all(self):
        """Close all connections in the pool."""
        async with self._lock:
            for conn in self._connections.values():
                await conn.close()
            self._connections.clear()


class ConnectionManager:
    """Manages connection lifecycle and pooling."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._pool = ConnectionPool(max_size=config.metadata.get("pool_size", 10))
        self._retry_count = 0
    
    async def create_connection(self, uri: str) -> Connection:
        """Create a new connection with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"Connection attempt {attempt + 1} for {uri}")
                
                # Get connection from pool
                connection = await self._pool.get_connection(uri, self.config)
                
                # Test the connection
                await self._test_connection(connection)
                
                logger.info(f"Connection established to {uri}")
                return connection
                
            except Exception as e:
                last_error = e
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.debug(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        
        raise ConnectionError(f"Failed to connect after {self.config.max_retries + 1} attempts: {last_error}")
    
    async def _test_connection(self, connection: Connection) -> None:
        """Test if a connection is working."""
        try:
            # Send a simple ping/health check
            await asyncio.wait_for(
                connection.transport.ping(),
                timeout=self.config.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Connection test timed out after {self.config.timeout} seconds")
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}")
    
    async def close(self):
        """Close all connections."""
        await self._pool.close_all()
    
    @asynccontextmanager
    async def get_connection(self, uri: str):
        """Context manager for getting a connection."""
        connection = await self.create_connection(uri)
        try:
            yield connection
        finally:
            # Connection will be returned to pool, not closed
            pass


class ReconnectingConnection:
    """A connection wrapper that automatically reconnects."""
    
    def __init__(self, manager: ConnectionManager, uri: str):
        self.manager = manager
        self.uri = uri
        self._connection: Optional[Connection] = None
        self._reconnect_lock = asyncio.Lock()
    
    async def _ensure_connected(self):
        """Ensure we have a valid connection."""
        if self._connection and not self._connection.closed:
            # Check health
            health = await self._connection.health_check()
            if health.status == "healthy":
                return
        
        # Need to reconnect
        async with self._reconnect_lock:
            # Double-check after acquiring lock
            if self._connection and not self._connection.closed:
                health = await self._connection.health_check()
                if health.status == "healthy":
                    return
            
            # Close old connection
            if self._connection:
                await self._connection.close()
            
            # Create new connection
            self._connection = await self.manager.create_connection(self.uri)
    
    async def send(self, data: Dict[str, Any]) -> None:
        """Send data with automatic reconnection."""
        await self._ensure_connected()
        await self._connection.send(data)
    
    async def receive(self) -> Dict[str, Any]:
        """Receive data with automatic reconnection."""
        await self._ensure_connected()
        return await self._connection.receive()
    
    async def close(self) -> None:
        """Close the connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None