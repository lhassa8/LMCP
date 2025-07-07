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
        console.print("  [cyan]lmcp install wikipedia[/cyan]       # Install a server")
        console.print("  [cyan]lmcp test wikipedia[/cyan]          # Test if a server works")
        console.print("  [cyan]lmcp inspect wikipedia[/cyan]       # Discover tools and parameters")
        console.print("  [cyan]lmcp examples wikipedia[/cyan]      # Show usage examples")
        console.print("\n[bold]🔧 Using Servers:[/bold]")
        console.print("  [cyan]lmcp use filesystem list_directory --params '{\"path\": \".\"}'[/cyan]")
        console.print("  [cyan]lmcp use wikipedia findPage --params '{\"query\": \"python\"}'[/cyan]")
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
def inspect(name: str) -> None:
    """Inspect a server to discover its tools and parameters."""
    client = SimpleMCP()
    
    async def do_inspect():
        result = await client.inspect_server(name)
        
        if "error" in result:
            console.print(f"❌ Error: {result['error']}")
            return
        
        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            
            console.print(f"[bold green]🔍 {name} Server Tools[/bold green]\n")
            
            for tool in tools:
                console.print(f"[bold cyan]🔧 {tool['name']}[/bold cyan]")
                console.print(f"   📝 {tool.get('description', 'No description')}")
                
                # Show input schema
                if 'inputSchema' in tool:
                    schema = tool['inputSchema']
                    if 'properties' in schema:
                        console.print("   📥 [bold]Parameters:[/bold]")
                        
                        required = schema.get('required', [])
                        for param_name, param_info in schema['properties'].items():
                            param_type = param_info.get('type', 'unknown')
                            param_desc = param_info.get('description', 'No description')
                            required_mark = " [red](required)[/red]" if param_name in required else " [dim](optional)[/dim]"
                            
                            console.print(f"      • [yellow]{param_name}[/yellow] ({param_type}){required_mark}")
                            console.print(f"        {param_desc}")
                        
                        # Generate example command
                        example_params = {}
                        for param_name, param_info in schema['properties'].items():
                            param_type = param_info.get('type', 'string')
                            if param_type == 'string':
                                example_params[param_name] = f"example_{param_name}"
                            elif param_type == 'number' or param_type == 'integer':
                                example_params[param_name] = 42
                            elif param_type == 'boolean':
                                example_params[param_name] = True
                            else:
                                example_params[param_name] = f"example_{param_name}"
                        
                        params_json = json.dumps(example_params)
                        console.print(f"   💡 [bold]Example:[/bold]")
                        console.print(f"      [cyan]lmcp use {name} {tool['name']} --params '{params_json}'[/cyan]")
                    else:
                        console.print("   📥 [bold]Parameters:[/bold] None required")
                        console.print(f"   💡 [bold]Example:[/bold]")
                        console.print(f"      [cyan]lmcp use {name} {tool['name']}[/cyan]")
                else:
                    console.print("   📥 [bold]Parameters:[/bold] Schema not available")
                
                console.print()  # Empty line between tools
                
        else:
            console.print("❌ No tools found or invalid response")
    
    asyncio.run(do_inspect())


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
            ("Echo message", 'lmcp use hello-world echo --params \'{"message": "Hello LMCP"}\''),
            ("Debug info", 'lmcp use hello-world debug --params \'{}\''),
        ],
        "wikipedia": [
            ("Search articles", 'lmcp use wikipedia findPage --params \'{"query": "artificial intelligence"}\''),
            ("Get page content", 'lmcp use wikipedia getPage --params \'{"title": "Python (programming language)"}\''),
            ("Today in history", 'lmcp use wikipedia onThisDay --params \'{"date": "2025-07-06"}\''),
        ],
        "sequential-thinking": [
            ("Think step by step", 'lmcp use sequential-thinking sequentialthinking --params \'{"thought": "How to solve this problem", "thoughtNumber": 1, "totalThoughts": 3, "nextThoughtNeeded": true}\''),
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
    """Use a tool on a server.
    
    Examples:
    lmcp use wikipedia findPage --params '{"query": "python"}'
    lmcp use filesystem read_file --params '{"path": "README.md"}'
    """
    client = SimpleMCP()
    
    # Parse parameters
    tool_params = {}
    if params:
        try:
            tool_params = json.loads(params)
        except json.JSONDecodeError:
            console.print("❌ Invalid JSON parameters")
            console.print("💡 Parameters must be valid JSON, like: --params '{\"query\": \"python\"}'")
            return
    else:
        # Try to get tool schema to provide better guidance
        async def check_params():
            schema_result = await client.get_tool_schema(server_name, tool_name)
            if "tool" in schema_result:
                tool = schema_result["tool"]
                if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                    required = tool["inputSchema"].get("required", [])
                    if required:
                        console.print(f"💡 The [bold]{tool_name}[/bold] tool requires parameters:")
                        for param in required:
                            param_info = tool["inputSchema"]["properties"].get(param, {})
                            param_type = param_info.get("type", "unknown")
                            param_desc = param_info.get("description", "No description")
                            console.print(f"   • [yellow]{param}[/yellow] ({param_type}): {param_desc}")
                        
                        console.print(f"\n   [cyan]lmcp inspect {server_name}[/cyan] - to see full tool details")
                        return
            
            # Fallback to generic message
            console.print(f"💡 The {tool_name} tool may need parameters. Try:")
            console.print(f"   [cyan]lmcp inspect {server_name}[/cyan] - to discover required parameters")
            console.print(f"   [cyan]lmcp examples {server_name}[/cyan] - to see examples")
        
        asyncio.run(check_params())
    
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