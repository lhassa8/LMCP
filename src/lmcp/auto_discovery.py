"""
Automated MCP Server Discovery System

This module provides functionality to automatically discover MCP servers
from GitHub, npm, and other sources.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from dataclasses import asdict

from .discovery import ServerInfo

logger = logging.getLogger(__name__)

class AutoServerDiscovery:
    """Automatically discover MCP servers from various sources."""
    
    def __init__(self):
        self.discovered_servers: Dict[str, ServerInfo] = {}
    
    async def scan_github(self, query: str = "mcp server") -> List[ServerInfo]:
        """Scan GitHub for MCP servers."""
        # This would use GitHub API to search for repositories
        # For now, return empty list as we'd need API keys
        logger.info(f"Would scan GitHub for: {query}")
        return []
    
    async def scan_npm(self, query: str = "mcp") -> List[ServerInfo]:
        """Scan npm registry for MCP packages."""
        # This would use npm registry API
        logger.info(f"Would scan npm for: {query}")
        return []
    
    async def discover_from_awesome_lists(self) -> List[ServerInfo]:
        """Discover servers from awesome-mcp-servers repositories."""
        discovered = []
        
        # URLs of known awesome lists
        awesome_lists = [
            "https://raw.githubusercontent.com/wong2/awesome-mcp-servers/main/README.md",
            "https://raw.githubusercontent.com/TensorBlock/awesome-mcp-servers/main/README.md",
        ]
        
        for url in awesome_lists:
            try:
                # Would fetch and parse markdown files
                logger.info(f"Would parse awesome list: {url}")
                # servers = await self._parse_awesome_list(url)
                # discovered.extend(servers)
            except Exception as e:
                logger.warning(f"Failed to parse {url}: {e}")
        
        return discovered
    
    async def _parse_awesome_list(self, url: str) -> List[ServerInfo]:
        """Parse an awesome list markdown file for server information."""
        # Implementation would:
        # 1. Fetch the markdown content
        # 2. Parse for server entries
        # 3. Extract name, description, repository
        # 4. Guess installation commands
        # 5. Create ServerInfo objects
        return []
    
    def save_discovered_servers(self, filename: str = "discovered_servers.json") -> None:
        """Save discovered servers to a JSON file."""
        data = {
            name: asdict(server) 
            for name, server in self.discovered_servers.items()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(self.discovered_servers)} servers to {filename}")
    
    def load_discovered_servers(self, filename: str = "discovered_servers.json") -> None:
        """Load discovered servers from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            for name, server_data in data.items():
                self.discovered_servers[name] = ServerInfo(**server_data)
            
            logger.info(f"Loaded {len(self.discovered_servers)} servers from {filename}")
        except FileNotFoundError:
            logger.info(f"No discovered servers file found: {filename}")
        except Exception as e:
            logger.error(f"Failed to load discovered servers: {e}")

async def auto_discover_servers() -> Dict[str, ServerInfo]:
    """Run automatic server discovery process."""
    discovery = AutoServerDiscovery()
    
    # Load any previously discovered servers
    discovery.load_discovered_servers()
    
    # Run discovery from various sources
    github_servers = await discovery.scan_github()
    npm_servers = await discovery.scan_npm()
    awesome_servers = await discovery.discover_from_awesome_lists()
    
    # Combine all discovered servers
    all_discovered = github_servers + npm_servers + awesome_servers
    
    # Add to registry (avoid duplicates)
    for server in all_discovered:
        if server.name not in discovery.discovered_servers:
            discovery.discovered_servers[server.name] = server
    
    # Save updated registry
    discovery.save_discovered_servers()
    
    return discovery.discovered_servers

# CLI command integration
async def scan_for_new_servers() -> int:
    """CLI command to scan for new MCP servers."""
    logger.info("Starting automatic server discovery...")
    
    try:
        discovered = await auto_discover_servers()
        print(f"✅ Discovery complete! Found {len(discovered)} servers total.")
        
        if discovered:
            print("\n🔍 Recently discovered servers:")
            for name, server in list(discovered.items())[:10]:  # Show first 10
                print(f"  • {name}: {server.description}")
            
            if len(discovered) > 10:
                print(f"  ... and {len(discovered) - 10} more!")
        
        return 0
    
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        print(f"❌ Discovery failed: {e}")
        return 1