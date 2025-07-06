"""
LMCP Command Line Interface

MCP Client for discovering and using existing MCP servers.
"""

import asyncio
import json
import logging
import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import __version__
from .simple_client import SimpleMCP

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """LMCP - MCP Client for discovering and using existing MCP servers."""
    # Set up logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    
    # If no command is provided, show quick help
    if ctx.invoked_subcommand is None:
        console.print("[bold green]🚀 LMCP - MCP Client & Server Discovery[/bold green]\n")
        console.print("[bold]🌐 Server Discovery:[/bold]")
        console.print("  [cyan]lmcp list[/cyan]                    # List available MCP servers")
        console.print("  [cyan]lmcp install filesystem[/cyan]     # Install a server")
        console.print("  [cyan]lmcp test filesystem[/cyan]        # Test if a server works")
        console.print("\n[bold]🔧 Using Servers:[/bold]")
        console.print("  [cyan]lmcp use filesystem list_directory --params '{\"path\": \".\"}'[/cyan]")
        console.print("\n[bold]📚 Help:[/bold]")
        console.print("  [cyan]lmcp --help[/cyan]       # Full help")
        console.print("  [cyan]lmcp version[/cyan]      # Version info")
        console.print("\n💡 Focus: Discover and use existing MCP servers")


@cli.command()
def list() -> None:
    """List available MCP servers."""
    client = SimpleMCP()
    client.list_servers()


@cli.command()
@click.argument("name")
def install(name: str) -> None:
    """Install a server."""
    client = SimpleMCP()
    success = client.install_server(name)
    if success:
        console.print(f"🚀 Test it: [cyan]lmcp test {name}[/cyan]")
    else:
        console.print("💡 Make sure Node.js and npm are installed")


@cli.command()
@click.argument("name")
def test(name: str) -> None:
    """Test if a server works."""
    client = SimpleMCP()
    
    async def do_test():
        success = await client.test_server(name)
        if success:
            console.print(f"🎉 {name} is ready to use!")
            console.print(f"💡 Try: [cyan]lmcp use {name} <tool-name>[/cyan]")
        else:
            console.print(f"💡 Try installing first: [cyan]lmcp install {name}[/cyan]")
    
    asyncio.run(do_test())


@cli.command()
@click.argument("server_name")
@click.argument("tool_name")
@click.option("--params", "-p", help="Tool parameters as JSON")
def use(server_name: str, tool_name: str, params: Optional[str]) -> None:
    """Use a tool on a server."""
    client = SimpleMCP()
    
    # Parse parameters
    tool_params = {}
    if params:
        try:
            tool_params = json.loads(params)
        except json.JSONDecodeError:
            console.print("❌ Invalid JSON parameters")
            return
    
    async def do_call():
        console.print(f"🔧 Using {tool_name} on {server_name}...")
        if tool_params:
            console.print(f"📝 Parameters: {tool_params}")
        
        result = await client.call_tool(server_name, tool_name, **tool_params)
        
        console.print("📋 Result:")
        if "error" in result:
            console.print(f"❌ Error: {result['error']}")
        else:
            console.print(json.dumps(result, indent=2))
    
    asyncio.run(do_call())


@cli.command()
def version() -> None:
    """Show LMCP version information."""
    console.print(f"[bold]LMCP[/bold] version [green]{__version__}[/green]")
    console.print("MCP Client for discovering and using existing MCP servers")
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