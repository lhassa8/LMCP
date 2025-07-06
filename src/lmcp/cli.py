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
        console.print("  [cyan]lmcp examples filesystem[/cyan]    # Show usage examples")
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
            console.print(f"💡 See examples: [cyan]lmcp examples {name}[/cyan]")
        else:
            console.print(f"💡 Try installing first: [cyan]lmcp install {name}[/cyan]")
    
    asyncio.run(do_test())


@cli.command()
@click.argument("name")
def examples(name: str) -> None:
    """Show usage examples for a server."""
    client = SimpleMCP()
    if name not in client.servers:
        console.print(f"❌ Server '{name}' not found")
        console.print("💡 Run [cyan]lmcp list[/cyan] to see available servers")
        return
    
    server = client.servers[name]
    
    # Server-specific examples
    examples_map = {
        "filesystem": [
            ("List directory", 'lmcp use filesystem list_directory --params \'{"path": "."}\''),
            ("Read file", 'lmcp use filesystem read_file --params \'{"path": "README.md"}\''),
            ("Write file", 'lmcp use filesystem write_file --params \'{"path": "test.txt", "content": "Hello World"}\''),
            ("Create directory", 'lmcp use filesystem create_directory --params \'{"path": "new_folder"}\''),
        ],
        "hello-world": [
            ("Echo message", 'lmcp use hello-world echo --params \'{"message": "Hello LMCP!"}\''),
            ("Add numbers", 'lmcp use hello-world add --params \'{"a": 5, "b": 3}\''),
            ("Debug info", 'lmcp use hello-world debug --params \'{}\''),
        ],
        "wikipedia": [
            ("Search articles", 'lmcp use wikipedia findPage --params \'{"query": "artificial intelligence"}\''),
            ("Get page content", 'lmcp use wikipedia getPage --params \'{"title": "Python (programming language)"}\''),
            ("Today in history", 'lmcp use wikipedia onThisDay --params \'{"month": 7, "day": 6}\''),
        ],
        "sequential-thinking": [
            ("Think step by step", 'lmcp use sequential-thinking sequentialthinking --params \'{"thought": "How to solve this problem"}\''),
        ],
        "calculator": [
            ("Basic calculation", 'lmcp use calculator calculate --params \'{"expression": "2 + 2 * 3"}\''),
        ],
        "dad-jokes": [
            ("Get random joke", 'lmcp use dad-jokes getJoke --params \'{}\''),
        ],
        "code-runner": [
            ("Run Python code", 'lmcp use code-runner run --params \'{"language": "python", "code": "print(\\"Hello World\\")"}\''),
        ],
        "kubernetes": [
            ("List pods", 'lmcp use kubernetes kubectl --params \'{"command": "get pods"}\''),
            ("Get services", 'lmcp use kubernetes kubectl --params \'{"command": "get services"}\''),
        ],
        "mysql": [
            ("Execute query", 'lmcp use mysql query --params \'{"sql": "SELECT * FROM users LIMIT 5"}\''),
        ],
        "desktop-commander": [
            ("Run terminal command", 'lmcp use desktop-commander exec --params \'{"command": "ls -la"}\''),
            ("Edit file", 'lmcp use desktop-commander edit --params \'{"file": "test.txt", "content": "Hello"}\''),
        ],
        "gmail": [
            ("List emails", 'lmcp use gmail listEmails --params \'{"maxResults": 10}\''),
            ("Send email", 'lmcp use gmail sendEmail --params \'{"to": "example@domain.com", "subject": "Test", "body": "Hello"}\''),
        ],
        "figma": [
            ("Get file info", 'lmcp use figma getFile --params \'{"fileId": "your-file-id"}\''),
            ("List projects", 'lmcp use figma getProjects --params \'{}\''),
        ],
        "jsonresume": [
            ("Get resume", 'lmcp use jsonresume getResume --params \'{}\''),
            ("Update resume", 'lmcp use jsonresume updateResume --params \'{"section": "basics", "data": {}}\''),
        ],
        "filesystem-secure": [
            ("List directory (secure)", 'lmcp use filesystem-secure list --params \'{"path": "."}\''),
            ("Read file (secure)", 'lmcp use filesystem-secure read --params \'{"path": "README.md"}\''),
        ],
        "filesystem-advanced": [
            ("Search and replace", 'lmcp use filesystem-advanced searchReplace --params \'{"path": ".", "search": "old", "replace": "new"}\''),
            ("Batch operations", 'lmcp use filesystem-advanced batchOp --params \'{"operation": "rename", "pattern": "*.txt"}\''),
        ],
        "supergateway": [
            ("Proxy request", 'lmcp use supergateway proxy --params \'{"url": "http://localhost:3000", "method": "GET"}\''),
        ],
        "elasticsearch": [
            ("Search index", 'lmcp use elasticsearch search --params \'{"index": "my-index", "query": "test"}\''),
            ("Create document", 'lmcp use elasticsearch index --params \'{"index": "my-index", "document": {"title": "Test"}}\''),
        ],
        "basic-mcp": [
            ("Basic operation", 'lmcp use basic-mcp hello --params \'{"name": "World"}\''),
        ],
    }
    
    console.print(f"[bold green]📋 Examples for {name}[/bold green]\n")
    console.print(f"[bold]📝 Description:[/bold] {server.description}")
    console.print(f"[bold]📦 Install:[/bold] [cyan]lmcp install {name}[/cyan]")
    console.print(f"[bold]🧪 Test:[/bold] [cyan]lmcp test {name}[/cyan]\n")
    
    if name in examples_map:
        console.print("[bold]💡 Usage Examples:[/bold]")
        for desc, cmd in examples_map[name]:
            console.print(f"  [yellow]#{desc}[/yellow]")
            console.print(f"  [cyan]{cmd}[/cyan]\n")
    else:
        console.print("[yellow]⚠️  No examples available yet for this server[/yellow]")
        console.print("💡 Try: [cyan]lmcp test {name}[/cyan] to see available tools")


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