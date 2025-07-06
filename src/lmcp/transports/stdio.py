"""
STDIO Transport Implementation

Provides communication over standard input/output.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional
from asyncio import StreamReader, StreamWriter

from .base import Transport
from ..exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class StdioTransport(Transport):
    """Transport implementation using standard input/output."""
    
    def __init__(self, config):
        super().__init__(config)
        self._reader: Optional[StreamReader] = None
        self._writer: Optional[StreamWriter] = None
        self._process: Optional[asyncio.subprocess.Process] = None
        self._command: Optional[str] = None
    
    async def connect(self, uri: str) -> None:
        """Connect to a process using stdio."""
        if self._connected:
            return
        
        try:
            # Parse the URI to get command
            # Format: stdio://command or stdio:///path/to/executable
            if uri.startswith("stdio://"):
                self._command = uri[8:]  # Remove "stdio://" prefix
            else:
                raise ConnectionError(f"Invalid stdio URI: {uri}")
            
            logger.debug(f"Starting process: {self._command}")
            
            # Start the process
            self._process = await asyncio.create_subprocess_shell(
                self._command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self._reader = self._process.stdout
            self._writer = self._process.stdin
            
            self._connected = True
            logger.info(f"Connected to process via stdio: {self._command}")
            
        except Exception as e:
            logger.error(f"Failed to connect via stdio: {e}")
            raise ConnectionError(f"Failed to connect via stdio: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the process."""
        if not self._connected:
            return
        
        try:
            # Close streams
            if self._writer:
                self._writer.close()
                await self._writer.wait_closed()
            
            # Terminate process
            if self._process:
                self._process.terminate()
                try:
                    await asyncio.wait_for(self._process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Process didn't terminate gracefully, killing...")
                    self._process.kill()
                    await self._process.wait()
            
            self._connected = False
            logger.info("Disconnected from stdio process")
            
        except Exception as e:
            logger.error(f"Error during stdio disconnect: {e}")
            raise ConnectionError(f"Failed to disconnect: {e}")
    
    async def send(self, data: Dict[str, Any]) -> None:
        """Send JSON data to the process."""
        if not self._connected or not self._writer:
            raise ConnectionError("Not connected")
        
        try:
            # Serialize to JSON and add newline
            json_data = json.dumps(data) + "\n"
            
            # Write to stdin
            self._writer.write(json_data.encode('utf-8'))
            await self._writer.drain()
            
            logger.debug(f"Sent data: {json_data.strip()}")
            
        except Exception as e:
            logger.error(f"Failed to send data: {e}")
            raise ConnectionError(f"Send failed: {e}")
    
    async def receive(self) -> Dict[str, Any]:
        """Receive JSON data from the process."""
        if not self._connected or not self._reader:
            raise ConnectionError("Not connected")
        
        try:
            # Read a line from stdout
            line = await asyncio.wait_for(
                self._reader.readline(),
                timeout=self.config.timeout
            )
            
            if not line:
                raise ConnectionError("Process closed stdout")
            
            # Decode and parse JSON
            json_str = line.decode('utf-8').strip()
            data = json.loads(json_str)
            
            logger.debug(f"Received data: {json_str}")
            return data
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Receive timeout after {self.config.timeout} seconds")
        except json.JSONDecodeError as e:
            raise ConnectionError(f"Invalid JSON received: {e}")
        except Exception as e:
            logger.error(f"Failed to receive data: {e}")
            raise ConnectionError(f"Receive failed: {e}")
    
    async def ping(self) -> None:
        """Send a ping message."""
        if not self._connected:
            raise ConnectionError("Not connected")
        
        # For stdio, we can just check if the process is alive
        if self._process and self._process.returncode is not None:
            raise ConnectionError("Process has terminated")
        
        # Send a simple ping message
        ping_msg = {
            "jsonrpc": "2.0",
            "method": "ping",
            "id": "ping"
        }
        
        await self.send(ping_msg)