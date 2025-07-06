"""
Test-Api API MCP Server

API proxy server template generated with LMCP.
"""

import lmcp
import httpx
from typing import Dict, Any, Optional

@lmcp.server("test-api")
class TestapiApiServer:
    """API proxy MCP server."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.example.com"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )
    
    @lmcp.tool("Make GET request")
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        response = await self.client.get(endpoint, params=params or {})
        response.raise_for_status()
        return response.json()
    
    @lmcp.tool("Make POST request") 
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the API."""
        response = await self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    
    @lmcp.tool("Check API status")
    async def status(self) -> Dict[str, Any]:
        """Check API status."""
        try:
            response = await self.client.get("/health")
            return {
                "status": "healthy",
                "response_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @lmcp.resource("api://info", description="API information")
    def api_info(self) -> Dict[str, Any]:
        """Get API information."""
        return {
            "base_url": self.base_url,
            "name": "test-api",
            "type": "api_proxy"
        }

if __name__ == "__main__":
    print("🌐 Starting test-api API server...")
    server = TestapiApiServer()
    lmcp.run_server(server)
