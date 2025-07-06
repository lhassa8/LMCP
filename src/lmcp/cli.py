"""
LMCP Command Line Interface

Provides a CLI for interacting with MCP servers and managing LMCP.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from rich.panel import Panel

from . import __version__
from .client import Client, connect
from .server import Server, run_server
from .types import ConnectionConfig
from .exceptions import LMCPError
from .discovery import list_servers, get_categories, get_server_info, test_server_availability, install_server, MCPServerRegistry

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """LMCP - Lightweight Model Context Protocol wrapper."""
    # Set up logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    
    # If no command is provided, show quick help
    if ctx.invoked_subcommand is None:
        console.print("[bold green]🚀 LMCP - Lightweight Model Context Protocol[/bold green]\n")
        console.print("Get started in 30 seconds:")
        console.print("  [cyan]lmcp create sample my-server[/cyan]  # Create a sample server")
        console.print("  [cyan]lmcp client list-tools \"stdio://python my_server_server.py\"[/cyan]  # Test it")
        console.print("\nMore commands:")
        console.print("  [cyan]lmcp --help[/cyan]     # Full help")
        console.print("  [cyan]lmcp version[/cyan]    # Version info")
        console.print("\n💡 Put URIs in quotes to avoid shell issues!")


@cli.group()
def client() -> None:
    """Client commands for connecting to MCP servers."""
    pass


@client.command()
@click.argument("uri")
@click.option("--timeout", "-t", default=30.0, help="Connection timeout in seconds")
@click.option("--format", "-f", type=click.Choice(["json", "table"]), default="table", help="Output format")
@click.pass_context
def connect_cmd(ctx: click.Context, uri: str, timeout: float, format: str) -> None:
    """Connect to an MCP server and show server info."""
    async def _connect():
        try:
            config = ConnectionConfig(uri=uri, timeout=timeout)
            
            console.print(f"[blue]Connecting to MCP server:[/blue] {uri}")
            
            async with Client(uri, config) as client:
                server_info = client.server_info
                
                if format == "json":
                    console.print(JSON(server_info.model_dump()))
                else:
                    table = Table(title="Server Information")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="green")
                    
                    table.add_row("Name", server_info.name)
                    table.add_row("Version", server_info.version)
                    table.add_row("Description", server_info.description or "N/A")
                    
                    console.print(table)
                    
                    # Show capabilities
                    if server_info.capabilities:
                        console.print("\n[bold]Capabilities:[/bold]")
                        console.print(JSON(server_info.capabilities))
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(_connect())


@client.command()
@click.argument("uri")
@click.option("--timeout", "-t", default=30.0, help="Connection timeout in seconds")
@click.option("--format", "-f", type=click.Choice(["json", "table"]), default="table", help="Output format")
@click.pass_context
def list_tools(ctx: click.Context, uri: str, timeout: float, format: str) -> None:
    """List available tools on an MCP server."""
    async def _list_tools():
        try:
            config = ConnectionConfig(uri=uri, timeout=timeout)
            
            async with Client(uri, config) as client:
                tools = await client.list_tools()
                
                if format == "json":
                    tools_data = [tool.model_dump() for tool in tools]
                    import json
                    console.print(json.dumps({"tools": tools_data}, indent=2))
                else:
                    if not tools:
                        console.print("[yellow]No tools available[/yellow]")
                        return
                    
                    table = Table(title="Available Tools")
                    table.add_column("Name", style="cyan")
                    table.add_column("Description", style="green")
                    
                    for tool in tools:
                        table.add_row(
                            tool.name,
                            tool.description or "No description"
                        )
                    
                    console.print(table)
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            
            # Provide helpful suggestions for common issues
            error_str = str(e).lower()
            if any(word in error_str for word in ["connection", "timeout", "failed to connect", "initialize", "stdio"]):
                console.print("\n[yellow]💡 Troubleshooting tips:[/yellow]")
                console.print("   • Make sure the server file exists and runs without errors")
                console.print("   • Try putting the URI in quotes: \"stdio://python server.py\"")
                console.print("   • Check if the server prints any startup messages (they can interfere with stdio)")
                console.print("   • Verify the Python path is correct")
            
            sys.exit(1)
    
    asyncio.run(_list_tools())


@client.command()
@click.argument("uri")
@click.argument("tool_name")
@click.option("--args", "-a", multiple=True, help="Tool arguments in key=value format")
@click.option("--timeout", "-t", default=30.0, help="Connection timeout in seconds")
@click.option("--format", "-f", type=click.Choice(["json", "text"]), default="text", help="Output format")
@click.pass_context
def call_tool(ctx: click.Context, uri: str, tool_name: str, args: List[str], timeout: float, format: str) -> None:
    """Call a tool on an MCP server."""
    async def _call_tool():
        try:
            # Parse arguments
            kwargs = {}
            for arg in args:
                if "=" not in arg:
                    console.print(f"[red]Error:[/red] Invalid argument format: {arg}")
                    console.print("Use: key=value")
                    sys.exit(1)
                
                key, value = arg.split("=", 1)
                # Try to parse as JSON, fall back to string
                try:
                    kwargs[key] = json.loads(value)
                except json.JSONDecodeError:
                    kwargs[key] = value
            
            config = ConnectionConfig(uri=uri, timeout=timeout)
            
            console.print(f"[blue]Calling tool:[/blue] {tool_name}")
            if kwargs:
                console.print(f"[blue]Arguments:[/blue] {kwargs}")
            
            async with Client(uri, config) as client:
                result = await client.call_tool(tool_name, **kwargs)
                
                if format == "json":
                    console.print(JSON(result.model_dump()))
                else:
                    if result.is_error:
                        console.print(f"[red]Tool Error:[/red] {result.error_message}")
                    else:
                        console.print(Panel(str(result.content), title="Tool Result"))
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(_call_tool())


@client.command()
@click.argument("uri")
@click.option("--timeout", "-t", default=30.0, help="Connection timeout in seconds")
@click.option("--format", "-f", type=click.Choice(["json", "table"]), default="table", help="Output format")
@click.pass_context
def list_resources(ctx: click.Context, uri: str, timeout: float, format: str) -> None:
    """List available resources on an MCP server."""
    async def _list_resources():
        try:
            config = ConnectionConfig(uri=uri, timeout=timeout)
            
            async with Client(uri, config) as client:
                resources = await client.list_resources()
                
                if format == "json":
                    resources_data = [resource.model_dump() for resource in resources]
                    import json
                    console.print(json.dumps({"resources": resources_data}, indent=2))
                else:
                    if not resources:
                        console.print("[yellow]No resources available[/yellow]")
                        return
                    
                    table = Table(title="Available Resources")
                    table.add_column("URI", style="cyan")
                    table.add_column("Name", style="green")
                    table.add_column("MIME Type", style="yellow")
                    table.add_column("Description", style="white")
                    
                    for resource in resources:
                        table.add_row(
                            resource.uri,
                            resource.name or "N/A",
                            resource.mime_type or "N/A",
                            resource.description or "No description"
                        )
                    
                    console.print(table)
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(_list_resources())


@cli.group()
def server() -> None:
    """Server commands for running MCP servers."""
    pass


@server.command()
@click.argument("module_path")
@click.option("--host", "-h", default="localhost", help="Host to bind to")
@click.option("--port", "-p", default=8080, help="Port to bind to")
@click.option("--name", "-n", help="Server name")
@click.pass_context
def run(ctx: click.Context, module_path: str, host: str, port: int, name: Optional[str]) -> None:
    """Run an MCP server from a Python module."""
    async def _run_server():
        try:
            # Import the module
            import importlib.util
            
            if ":" in module_path:
                module_name, server_name = module_path.split(":", 1)
            else:
                module_name = module_path
                server_name = "server"
            
            # Load module
            if "/" in module_name or module_name.endswith(".py"):
                # File path
                spec = importlib.util.spec_from_file_location("server_module", module_name)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Module name
                module = importlib.import_module(module_name)
            
            # Get server instance
            server_instance = getattr(module, server_name)
            
            if not isinstance(server_instance, Server):
                console.print(f"[red]Error:[/red] {server_name} is not a Server instance")
                sys.exit(1)
            
            console.print(f"[green]Starting MCP server:[/green] {server_instance.name}")
            console.print(f"[blue]Host:[/blue] {host}")
            console.print(f"[blue]Port:[/blue] {port}")
            
            await run_server(server_instance, host, port)
            
        except ImportError as e:
            console.print(f"[red]Import Error:[/red] {e}")
            sys.exit(1)
        except AttributeError as e:
            console.print(f"[red]Attribute Error:[/red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(_run_server())


@cli.group()
def config() -> None:
    """Configuration management commands."""
    pass


@cli.group() 
def create() -> None:
    """Create new servers and components quickly."""
    pass


@create.command()
@click.argument("name")
@click.option("--type", "-t", type=click.Choice(["basic", "database", "api"]), default="basic", help="Server type")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def server(name: str, type: str, output: Optional[str]) -> None:
    """Create a new MCP server from template."""
    from .utils.templates import ServerTemplate
    
    try:
        if type == "basic":
            code = ServerTemplate.basic_server(name)
        elif type == "database":
            code = ServerTemplate.database_server(name)
        elif type == "api":
            code = ServerTemplate.api_server(name)
        else:
            console.print(f"[red]Error:[/red] Unknown server type: {type}")
            sys.exit(1)
        
        # Determine output file
        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"{name.replace('-', '_')}_server.py")
        
        # Write the code
        output_path.write_text(code)
        
        console.print(f"[green]✅ Created {type} server:[/green] {output_path}")
        console.print(f"[blue]🚀 Run with:[/blue] python {output_path}")
        console.print(f"[blue]🧪 Test with:[/blue] lmcp client list-tools stdio://python {output_path}")
        
    except Exception as e:
        console.print(f"[red]Error creating server:[/red] {e}")
        sys.exit(1)


@create.command()
@click.argument("name") 
def sample(name: str) -> None:
    """Create a sample server to get started quickly."""
    from .utils.helpers import create_sample_server
    
    try:
        filename = create_sample_server(name)
        console.print(f"[green]🎉 Ready to go![/green] Run: [bold]python {filename}[/bold]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@config.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def init(output: Optional[str]) -> None:
    """Initialize a new LMCP configuration file."""
    config_data = {
        "connections": {
            "filesystem": {
                "uri": "stdio://mcp-server-filesystem",
                "description": "Local filesystem access"
            },
            "git": {
                "uri": "stdio://mcp-server-git", 
                "description": "Git repository access"
            }
        },
        "servers": {
            "example": {
                "name": "example-server",
                "description": "Example MCP server",
                "transport": "stdio"
            }
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    output_path = Path(output) if output else Path("lmcp.json")
    
    try:
        with open(output_path, "w") as f:
            json.dump(config_data, f, indent=2)
        
        console.print(f"[green]Configuration file created:[/green] {output_path}")
        
    except Exception as e:
        console.print(f"[red]Error creating config file:[/red] {e}")
        sys.exit(1)


@config.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file: str) -> None:
    """Validate an LMCP configuration file."""
    try:
        with open(config_file) as f:
            config_data = json.load(f)
        
        # Basic validation
        required_sections = ["connections", "servers"]
        for section in required_sections:
            if section not in config_data:
                console.print(f"[yellow]Warning:[/yellow] Missing section: {section}")
        
        console.print(f"[green]Configuration file is valid:[/green] {config_file}")
        
        # Show summary
        connections = config_data.get("connections", {})
        servers = config_data.get("servers", {})
        
        console.print(f"[blue]Connections:[/blue] {len(connections)}")
        console.print(f"[blue]Servers:[/blue] {len(servers)}")
        
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.group()
def discover() -> None:
    """Discover and manage MCP servers."""
    pass


@discover.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--search", "-s", help="Search servers by name or description")
@click.option("--verified", is_flag=True, help="Show only verified servers")
def list_available(category: str, search: str, verified: bool) -> None:
    """List available MCP servers."""
    servers = list_servers(category=category or "", search=search or "")
    
    if verified:
        servers = [s for s in servers if s.get("verified", False)]
    
    if not servers:
        console.print("[yellow]No servers found matching criteria[/yellow]")
        return
    
    table = Table(title="🌐 Available MCP Servers")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Verified", style="green")
    
    for server in servers:
        verified = "✅" if server["verified"] else "❓"
        table.add_row(
            server["name"],
            server["description"][:60] + "..." if len(server["description"]) > 60 else server["description"],
            server["category"],
            verified
        )
    
    console.print(table)
    console.print(f"\n💡 Use [cyan]lmcp discover info <name>[/cyan] for details")
    console.print(f"💡 Use [cyan]lmcp discover install <name>[/cyan] to install")


@discover.command()
def categories() -> None:
    """List available server categories."""
    cats = get_categories()
    
    console.print("[bold]📂 Server Categories:[/bold]\n")
    for category in sorted(cats):
        servers = list_servers(category=category)
        console.print(f"• [cyan]{category}[/cyan] ({len(servers)} servers)")


@discover.command()
@click.argument("name")
def info(name: str) -> None:
    """Show detailed information about a server."""
    server = get_server_info(name)
    
    if not server:
        console.print(f"[red]Server '{name}' not found[/red]")
        console.print("💡 Use [cyan]lmcp discover list[/cyan] to see available servers")
        return
    
    # Create info panel
    info_text = f"""[bold]{server['name']}[/bold]
📝 {server['description']}

📂 Category: {server['category']}
🏷️  Tags: {', '.join(server['tags'])}
✅ Verified: {'Yes' if server['verified'] else 'No'}

🔧 Tools: {', '.join(server['tools'][:5])}{'...' if len(server['tools']) > 5 else ''}
📁 Resources: {', '.join(server['resources'][:3]) if server['resources'] else 'None'}{'...' if server['resources'] and len(server['resources']) > 3 else ''}

🔗 Repository: {server['repository']}"""
    
    console.print(Panel(info_text, title=f"🌐 {server['name']}", border_style="cyan"))
    
    # Installation info
    console.print(f"\n[bold]📦 Installation:[/bold]")
    console.print(f"[yellow]{server['install_command']}[/yellow]")
    
    console.print(f"\n[bold]🚀 Usage:[/bold]")
    console.print(f"[yellow]{server['run_command']}[/yellow]")
    
    # Examples
    if server['examples']:
        console.print(f"\n[bold]💡 Examples:[/bold]")
        for example in server['examples']:
            console.print(f"[dim]{example}[/dim]")
    
    # Quick actions
    console.print(f"\n[bold]⚡ Quick Actions:[/bold]")
    console.print(f"• Install: [cyan]lmcp discover install {name}[/cyan]")
    console.print(f"• Test: [cyan]lmcp discover test {name}[/cyan]")


@discover.command()
@click.argument("name")
def install(name: str) -> None:
    """Install a server."""
    registry = MCPServerRegistry()
    server = registry.get_by_name(name)
    
    if not server:
        console.print(f"[red]Server '{name}' not found[/red]")
        return
    
    console.print(f"📦 Installing [cyan]{name}[/cyan]...")
    console.print(f"Command: [yellow]{server.install_command}[/yellow]")
    
    # Run installation
    async def do_install():
        result = await install_server(server)
        
        if result["success"]:
            console.print(f"✅ [green]{name} installed successfully![/green]")
            if result["output"]:
                console.print(f"Output: {result['output']}")
            
            console.print(f"\n🚀 Test it with:")
            console.print(f"[cyan]lmcp discover test {name}[/cyan]")
            
        else:
            console.print(f"❌ [red]Installation failed[/red]")
            if result["error"]:
                console.print(f"Error: {result['error']}")
    
    asyncio.run(do_install())


@discover.command()
@click.argument("name")
def test(name: str) -> None:
    """Test if a server is available and working."""
    registry = MCPServerRegistry()
    server = registry.get_by_name(name)
    
    if not server:
        console.print(f"[red]Server '{name}' not found[/red]")
        return
    
    console.print(f"🧪 Testing [cyan]{name}[/cyan]...")
    
    async def do_test():
        result = await test_server_availability(server)
        
        if result["available"]:
            console.print(f"✅ [green]{name} is working![/green]")
            console.print(f"⏱️  Connection time: {result['test_time']:.2f}s")
            
            if result["tools"]:
                console.print(f"🔧 Available tools: {', '.join(result['tools'][:5])}")
                if len(result['tools']) > 5:
                    console.print(f"   ... and {len(result['tools']) - 5} more")
                    
            console.print(f"\n💡 Use it in your code:")
            console.print(f"[dim]async with connect('{server.run_command}') as client:[/dim]")
            console.print(f"[dim]    tools = await client.list_tools()[/dim]")
            
        else:
            console.print(f"❌ [red]{name} is not available[/red]")
            if result["error"]:
                console.print(f"Error: {result['error']}")
                
                # Provide specific troubleshooting tips
                if "npx command not found" in result["error"]:
                    console.print("\n🔧 [yellow]Troubleshooting:[/yellow]")
                    console.print("1. Install Node.js: https://nodejs.org/")
                    console.print("2. Verify installation: [cyan]npx --version[/cyan]")
                    console.print("3. Then install the server: [cyan]lmcp discover install filesystem[/cyan]")
                elif "npx command failed" in result["error"]:
                    console.print("\n🔧 [yellow]Troubleshooting:[/yellow]")
                    console.print("1. Install the server package: [cyan]lmcp discover install filesystem[/cyan]")
                    console.print("2. Check Node.js version: [cyan]node --version[/cyan]")
                    console.print("3. Try reinstalling: [cyan]npm uninstall -g @modelcontextprotocol/server-filesystem && npm install -g @modelcontextprotocol/server-filesystem[/cyan]")
                elif "Invalid URI scheme" in result["error"]:
                    console.print("\n🔧 [yellow]Troubleshooting:[/yellow]")
                    console.print("This appears to be a configuration issue. Please report this bug.")
            
            console.print(f"\n💡 Try installing first:")
            console.print(f"[cyan]lmcp discover install {name}[/cyan]")
    
    asyncio.run(do_test())


@discover.command()
def scan() -> None:
    """Scan for new MCP servers automatically."""
    from .auto_discovery import scan_for_new_servers
    
    async def do_scan():
        return await scan_for_new_servers()
    
    result = asyncio.run(do_scan())
    sys.exit(result)


@discover.command()
@click.option("--category", "-c", help="Filter by category")
def browse(category: str) -> None:
    """Interactive browse mode for servers."""
    servers = list_servers(category=category or "")
    
    console.print("[bold]🌐 MCP Server Browser[/bold]\n")
    
    for i, server in enumerate(servers, 1):
        status = "✅" if server["verified"] else "❓"
        console.print(f"{i:2d}. {status} [cyan]{server['name']}[/cyan] - {server['description']}")
    
    console.print(f"\n💡 Use [cyan]lmcp discover info <name>[/cyan] for details")
    console.print(f"💡 Use [cyan]lmcp discover install <name>[/cyan] to install")


@cli.command()
def version() -> None:
    """Show LMCP version information."""
    console.print(f"[bold]LMCP[/bold] version [green]{__version__}[/green]")
    console.print("Lightweight Model Context Protocol wrapper")
    console.print("https://github.com/lhassa8/LMCP")


def main() -> None:
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()