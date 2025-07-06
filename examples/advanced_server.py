"""
Advanced LMCP Server Example

Demonstrates advanced server features including streaming, error handling,
validation, and complex resource management.
"""

import asyncio
import logging
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path

from lmcp import Server, tool, resource, prompt, run_server
from lmcp.types import ServerConfig


class DatabaseServer(Server):
    """Advanced database server with multiple features."""
    
    def __init__(self):
        config = ServerConfig(
            name="database-server",
            description="Advanced database server with SQLite backend",
            capabilities={
                "streaming": True,
                "transactions": True,
                "validation": True
            }
        )
        super().__init__(name="database-server", config=config)
        
        # Initialize database
        self.db_path = Path("example.db")
        self._init_database()
        
        # Transaction state
        self._active_transactions: Dict[str, sqlite3.Connection] = {}
    
    def _init_database(self):
        """Initialize the example database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                );
                
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                -- Insert sample data if empty
                INSERT OR IGNORE INTO users (id, username, email) VALUES 
                    (1, 'alice', 'alice@example.com'),
                    (2, 'bob', 'bob@example.com'),
                    (3, 'charlie', 'charlie@example.com');
                
                INSERT OR IGNORE INTO posts (id, user_id, title, content) VALUES
                    (1, 1, 'First Post', 'This is my first post!'),
                    (2, 1, 'Another Post', 'Here is another post with more content.'),
                    (3, 2, 'Bob''s Thoughts', 'Some thoughts from Bob.');
                
                INSERT OR IGNORE INTO comments (post_id, user_id, content) VALUES
                    (1, 2, 'Great post!'),
                    (1, 3, 'Thanks for sharing'),
                    (2, 3, 'Very interesting');
            """)
    
    # User Management Tools
    @tool("Create a new user")
    def create_user(self, username: str, email: str) -> Dict[str, Any]:
        """Create a new user in the database."""
        if not username or not email:
            raise ValueError("Username and email are required")
        
        if "@" not in email:
            raise ValueError("Invalid email format")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email) VALUES (?, ?)",
                    (username, email)
                )
                user_id = cursor.lastrowid
                
                return {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "created_at": datetime.now().isoformat(),
                    "message": "User created successfully"
                }
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                raise ValueError(f"Username '{username}' already exists")
            elif "email" in str(e):
                raise ValueError(f"Email '{email}' already exists")
            else:
                raise ValueError(f"Database constraint error: {e}")
    
    @tool("Get user information")
    def get_user(self, user_id: Optional[int] = None, username: Optional[str] = None) -> Dict[str, Any]:
        """Get user information by ID or username."""
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            else:
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError("User not found")
            
            return dict(row)
    
    @tool("List users with pagination")
    def list_users(self, page: int = 1, page_size: int = 10, active_only: bool = True) -> Dict[str, Any]:
        """List users with pagination support."""
        if page < 1:
            raise ValueError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")
        
        offset = (page - 1) * page_size
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Count total users
            where_clause = "WHERE is_active = 1" if active_only else ""
            cursor.execute(f"SELECT COUNT(*) FROM users {where_clause}")
            total_count = cursor.fetchone()[0]
            
            # Get page of users
            cursor.execute(f"""
                SELECT * FROM users {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (page_size, offset))
            
            users = [dict(row) for row in cursor.fetchall()]
            
            return {
                "users": users,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }
    
    # Post Management Tools
    @tool("Create a new post")
    def create_post(self, user_id: int, title: str, content: str = "") -> Dict[str, Any]:
        """Create a new post."""
        if not title.strip():
            raise ValueError("Title cannot be empty")
        
        # Verify user exists
        try:
            self.get_user(user_id=user_id)
        except ValueError:
            raise ValueError(f"User with ID {user_id} not found")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
                (user_id, title, content)
            )
            post_id = cursor.lastrowid
            
            return {
                "post_id": post_id,
                "user_id": user_id,
                "title": title,
                "content": content,
                "created_at": datetime.now().isoformat(),
                "message": "Post created successfully"
            }
    
    @tool("Search posts")
    def search_posts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search posts by title or content."""
        if not query.strip():
            raise ValueError("Search query cannot be empty")
        
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search in title and content
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT p.*, u.username 
                FROM posts p 
                JOIN users u ON p.user_id = u.id
                WHERE p.title LIKE ? OR p.content LIKE ?
                ORDER BY p.created_at DESC
                LIMIT ?
            """, (search_pattern, search_pattern, limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
    
    @tool("Get post analytics")
    def get_post_analytics(self, post_id: int) -> Dict[str, Any]:
        """Get analytics for a specific post."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get post info
            cursor.execute("""
                SELECT p.*, u.username
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = ?
            """, (post_id,))
            
            post = cursor.fetchone()
            if not post:
                raise ValueError(f"Post with ID {post_id} not found")
            
            # Get comment count
            cursor.execute("SELECT COUNT(*) FROM comments WHERE post_id = ?", (post_id,))
            comment_count = cursor.fetchone()[0]
            
            # Get recent comments
            cursor.execute("""
                SELECT c.content, c.created_at, u.username
                FROM comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.post_id = ?
                ORDER BY c.created_at DESC
                LIMIT 5
            """, (post_id,))
            
            recent_comments = [dict(row) for row in cursor.fetchall()]
            
            return {
                "post": dict(post),
                "analytics": {
                    "view_count": post["view_count"],
                    "comment_count": comment_count,
                    "engagement_score": post["view_count"] + (comment_count * 5),
                    "days_since_created": (datetime.now() - datetime.fromisoformat(post["created_at"])).days
                },
                "recent_comments": recent_comments
            }
    
    # Transaction Tools
    @tool("Begin database transaction")
    def begin_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Begin a new database transaction."""
        if transaction_id in self._active_transactions:
            raise ValueError(f"Transaction {transaction_id} already active")
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("BEGIN")
        self._active_transactions[transaction_id] = conn
        
        return {
            "transaction_id": transaction_id,
            "status": "active",
            "message": "Transaction started"
        }
    
    @tool("Commit transaction")
    def commit_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Commit an active transaction."""
        if transaction_id not in self._active_transactions:
            raise ValueError(f"No active transaction: {transaction_id}")
        
        conn = self._active_transactions.pop(transaction_id)
        conn.commit()
        conn.close()
        
        return {
            "transaction_id": transaction_id,
            "status": "committed",
            "message": "Transaction committed successfully"
        }
    
    @tool("Rollback transaction")
    def rollback_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Rollback an active transaction."""
        if transaction_id not in self._active_transactions:
            raise ValueError(f"No active transaction: {transaction_id}")
        
        conn = self._active_transactions.pop(transaction_id)
        conn.rollback()
        conn.close()
        
        return {
            "transaction_id": transaction_id,
            "status": "rolled_back",
            "message": "Transaction rolled back"
        }
    
    # Resources
    @resource("db://schema", description="Database schema information", mime_type="application/json")
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [
                    {
                        "name": row[1],
                        "type": row[2],
                        "nullable": not row[3],
                        "primary_key": bool(row[5])
                    }
                    for row in cursor.fetchall()
                ]
                schema[table] = columns
            
            return {
                "database": str(self.db_path),
                "tables": tables,
                "schema": schema,
                "generated_at": datetime.now().isoformat()
            }
    
    @resource("db://stats", description="Database statistics", mime_type="application/json")
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database usage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Table row counts
            for table in ["users", "posts", "comments"]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at > datetime('now', '-7 days')
            """)
            stats["new_users_last_week"] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM posts 
                WHERE created_at > datetime('now', '-7 days')
            """)
            stats["new_posts_last_week"] = cursor.fetchone()[0]
            
            # Top users by post count
            cursor.execute("""
                SELECT u.username, COUNT(p.id) as post_count
                FROM users u
                LEFT JOIN posts p ON u.id = p.user_id
                GROUP BY u.id, u.username
                ORDER BY post_count DESC
                LIMIT 5
            """)
            stats["top_users"] = [
                {"username": row[0], "post_count": row[1]}
                for row in cursor.fetchall()
            ]
            
            return {
                "statistics": stats,
                "database_size_bytes": os.path.getsize(self.db_path),
                "active_transactions": len(self._active_transactions),
                "generated_at": datetime.now().isoformat()
            }
    
    # Prompts
    @prompt("data_analysis", description="Generate data analysis prompts")
    def data_analysis_prompt(self, focus: str = "general") -> List[Dict[str, str]]:
        """Generate prompts for data analysis tasks."""
        prompts = {
            "users": "Analyze user engagement patterns and growth trends in the database.",
            "posts": "Examine posting frequency, content length, and engagement metrics.",
            "activity": "Investigate recent activity patterns and identify peak usage times.",
            "general": "Perform a comprehensive analysis of the database content and user behavior."
        }
        
        prompt_text = prompts.get(focus, prompts["general"])
        
        return [
            {
                "role": "user",
                "content": f"Database Analysis Request:\n\n{prompt_text}\n\nPlease use the available database tools to gather information and provide insights."
            }
        ]
    
    @prompt("query_help", description="Help with database queries")
    def query_help_prompt(self, task: str = "general") -> List[Dict[str, str]]:
        """Generate help prompts for database operations."""
        help_content = {
            "users": "Here are the available user management operations:\n- create_user(username, email): Create a new user\n- get_user(user_id or username): Get user details\n- list_users(page, page_size, active_only): List users with pagination",
            "posts": "Here are the available post management operations:\n- create_post(user_id, title, content): Create a new post\n- search_posts(query, limit): Search posts by content\n- get_post_analytics(post_id): Get detailed post analytics",
            "transactions": "Here are the available transaction operations:\n- begin_transaction(transaction_id): Start a new transaction\n- commit_transaction(transaction_id): Commit changes\n- rollback_transaction(transaction_id): Rollback changes",
            "general": "This database server provides comprehensive user and post management with transaction support. Use the schema and stats resources to understand the data structure."
        }
        
        content = help_content.get(task, help_content["general"])
        
        return [
            {
                "role": "assistant",
                "content": f"Database Help - {task.title()}:\n\n{content}\n\nFor more information, check the 'db://schema' and 'db://stats' resources."
            }
        ]


async def main():
    """Run the advanced database server."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("🗄️  Starting Advanced Database MCP Server...")
    print("=" * 60)
    print("📊 Features:")
    print("  - Complete user and post management")
    print("  - Advanced search and analytics")
    print("  - Transaction support")
    print("  - Real-time statistics")
    print("  - Data validation and error handling")
    print("  - Pagination and performance optimization")
    print("  - SQLite backend with sample data")
    print()
    
    # Create and configure server
    server = DatabaseServer()
    
    print(f"🚀 Server: {server.config.name}")
    print(f"📝 Description: {server.config.description}")
    print(f"🔧 Tools: {len(server.list_tools())}")
    print(f"📁 Resources: {len(server.list_resources())}")
    print(f"💬 Prompts: {len(server.list_prompts())}")
    print(f"⚡ Capabilities: {', '.join(server.config.capabilities.keys())}")
    print()
    
    print("🔍 Available Operations:")
    for tool in server.list_tools():
        print(f"  - {tool.name}: {tool.description}")
    print()
    
    print("📁 Available Resources:")
    for resource in server.list_resources():
        print(f"  - {resource.uri}: {resource.description}")
    print()
    
    try:
        await run_server(server)
    except KeyboardInterrupt:
        print("\n👋 Database server stopped")
        
        # Clean up active transactions
        if hasattr(server, '_active_transactions'):
            for transaction_id, conn in server._active_transactions.items():
                conn.rollback()
                conn.close()
                print(f"🔄 Rolled back transaction: {transaction_id}")


if __name__ == "__main__":
    asyncio.run(main())