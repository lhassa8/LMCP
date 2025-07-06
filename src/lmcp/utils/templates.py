"""
Templates and code generation helpers for LMCP.
"""

from typing import Dict, Any, List
from pathlib import Path


class ServerTemplate:
    """Template for generating server code."""
    
    @staticmethod
    def basic_server(name: str, tools: List[Dict[str, Any]] = None) -> str:
        """
        Generate a basic server template.
        
        Args:
            name: Server name
            tools: List of tool specifications
            
        Returns:
            Python code as string
        """
        tools = tools or [
            {"name": "echo", "params": [{"name": "message", "type": "str"}], "return": "str"},
            {"name": "add", "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}], "return": "int"}
        ]
        
        code = f'''"""
{name.title()} MCP Server

Generated with LMCP ServerTemplate.
"""

import lmcp

@lmcp.server("{name}")
class {name.replace('-', '').replace('_', '').title()}Server:
    """Auto-generated MCP server."""
    
'''
        
        # Generate tools
        for tool in tools:
            params_str = ", ".join([f"{p['name']}: {p['type']}" for p in tool["params"]])
            tool_name = tool["name"]
            return_type = tool.get("return", "str")
            
            code += f'''    @lmcp.tool("{tool_name.title()} operation")
    def {tool_name}(self, {params_str}) -> {return_type}:
        """Auto-generated tool: {tool_name}."""
        # TODO: Implement {tool_name} logic
        raise NotImplementedError("Please implement {tool_name}")
    
'''
        
        # Add main block
        code += f'''
if __name__ == "__main__":
    print("🚀 Starting {name} server...")
    server = {name.replace('-', '').replace('_', '').title()}Server()
    lmcp.run_server(server)
'''
        
        return code
    
    @staticmethod
    def database_server(name: str, table_name: str = "items") -> str:
        """Generate a database server template."""
        return f'''"""
{name.title()} Database MCP Server

Database server template generated with LMCP.
"""

import lmcp
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

@lmcp.server("{name}")
class {name.replace('-', '').replace('_', '').title()}DatabaseServer:
    """Database MCP server."""
    
    def __init__(self):
        super().__init__()
        self.db_path = Path("{name}.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    @lmcp.tool("Create a new item")
    def create_item(self, name: str, value: str = "") -> Dict[str, Any]:
        """Create a new item in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO {table_name} (name, value) VALUES (?, ?)",
                (name, value)
            )
            item_id = cursor.lastrowid
            
            return {{
                "id": item_id,
                "name": name,
                "value": value,
                "message": "Item created successfully"
            }}
    
    @lmcp.tool("Get an item by ID")
    def get_item(self, item_id: int) -> Dict[str, Any]:
        """Get an item by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM {table_name} WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Item with ID {{item_id}} not found")
            
            return dict(row)
    
    @lmcp.tool("List all items")
    def list_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List all items with optional limit."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    @lmcp.resource("db://schema", description="Database schema")
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            return {{
                "table": "{table_name}",
                "columns": [
                    {{
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5])
                    }}
                    for col in columns
                ]
            }}

if __name__ == "__main__":
    print("🗄️  Starting {name} database server...")
    server = {name.replace('-', '').replace('_', '').title()}DatabaseServer()
    lmcp.run_server(server)
'''
    
    @staticmethod
    def api_server(name: str, base_url: str = "https://api.example.com") -> str:
        """Generate an API proxy server template."""
        return f'''"""
{name.title()} API MCP Server

API proxy server template generated with LMCP.
"""

import lmcp
import httpx
from typing import Dict, Any, Optional

@lmcp.server("{name}")
class {name.replace('-', '').replace('_', '').title()}ApiServer:
    """API proxy MCP server."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "{base_url}"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )
    
    @lmcp.tool("Make GET request")
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        response = await self.client.get(endpoint, params=params or {{}})
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
            return {{
                "status": "healthy",
                "response_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }}
        except Exception as e:
            return {{
                "status": "unhealthy",
                "error": str(e)
            }}
    
    @lmcp.resource("api://info", description="API information")
    def api_info(self) -> Dict[str, Any]:
        """Get API information."""
        return {{
            "base_url": self.base_url,
            "name": "{name}",
            "type": "api_proxy"
        }}

if __name__ == "__main__":
    print("🌐 Starting {name} API server...")
    server = {name.replace('-', '').replace('_', '').title()}ApiServer()
    lmcp.run_server(server)
'''


class ToolTemplate:
    """Template for generating individual tools."""
    
    @staticmethod
    def simple_tool(name: str, params: List[Dict[str, str]], return_type: str = "str") -> str:
        """Generate a simple tool function."""
        params_str = ", ".join([f"{p['name']}: {p['type']}" for p in params])
        
        return f'''@lmcp.tool("{name.replace('_', ' ').title()}")
def {name}(self, {params_str}) -> {return_type}:
    """Auto-generated tool: {name}."""
    # TODO: Implement {name} logic
    raise NotImplementedError("Please implement {name}")
'''
    
    @staticmethod
    def math_tool(operation: str) -> str:
        """Generate a math operation tool."""
        ops = {
            "add": ("a + b", "Add two numbers"),
            "subtract": ("a - b", "Subtract two numbers"), 
            "multiply": ("a * b", "Multiply two numbers"),
            "divide": ("a / b if b != 0 else float('inf')", "Divide two numbers"),
            "power": ("a ** b", "Raise a to the power of b")
        }
        
        if operation not in ops:
            raise ValueError(f"Unknown operation: {operation}")
        
        expr, desc = ops[operation]
        
        return f'''@lmcp.tool("{desc}")
def {operation}(self, a: float, b: float) -> float:
    """{desc}."""
    return {expr}
'''
    
    @staticmethod
    def file_tool(operation: str) -> str:
        """Generate a file operation tool."""
        ops = {
            "read": (
                "Path(filename).read_text()",
                "Read contents of a file",
                "filename: str"
            ),
            "write": (
                "Path(filename).write_text(content); return 'File written successfully'",
                "Write content to a file", 
                "filename: str, content: str"
            ),
            "list": (
                "[str(p) for p in Path(directory).glob('*')]",
                "List files in a directory",
                "directory: str = '.'"
            ),
            "exists": (
                "Path(filename).exists()",
                "Check if a file exists",
                "filename: str"
            )
        }
        
        if operation not in ops:
            raise ValueError(f"Unknown file operation: {operation}")
        
        expr, desc, params = ops[operation]
        
        return f'''@lmcp.tool("{desc}")
def {operation}_file(self, {params}) -> Any:
    """{desc}."""
    from pathlib import Path
    return {expr}
'''