"""
Base Transport Interface

Defines the interface for all MCP transports.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from ..types import ConnectionConfig, HealthStatus


class Transport(ABC):
    """Abstract base class for MCP transports."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._connected = False
    
    @abstractmethod
    async def connect(self, uri: str) -> None:
        """Connect to the server."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the server."""
        pass
    
    @abstractmethod
    async def send(self, data: Dict[str, Any]) -> None:
        """Send data to the server."""
        pass
    
    @abstractmethod
    async def receive(self) -> Dict[str, Any]:
        """Receive data from the server."""
        pass
    
    @abstractmethod
    async def ping(self) -> None:
        """Send a ping to test connectivity."""
        pass
    
    async def health_check(self) -> HealthStatus:
        """Check the health of the transport."""
        if not self._connected:
            return HealthStatus(
                status="unhealthy",
                last_check=datetime.now(),
                checks={"connection": "not connected"}
            )
        
        try:
            await self.ping()
            return HealthStatus(
                status="healthy",
                last_check=datetime.now(),
                checks={"connection": "ok", "ping": "ok"}
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                last_check=datetime.now(),
                checks={"connection": "error", "error": str(e)}
            )
    
    async def close(self) -> None:
        """Close the transport."""
        if self._connected:
            await self.disconnect()
    
    @property
    def connected(self) -> bool:
        """Check if transport is connected."""
        return self._connected