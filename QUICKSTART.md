# 🚀 LMCP Quick Start - Get Running in 2 Minutes!

LMCP makes working with the Model Context Protocol super easy. Here's how to get started instantly:

## 📦 Step 1: Set Up Environment (30 seconds)

```bash
# Create a clean Python environment (recommended!)
python -m venv lmcp-env

# Activate it
source lmcp-env/bin/activate  # On Windows: lmcp-env\Scripts\activate

# Install LMCP from GitHub (current method)
pip install git+https://github.com/lhassa8/LMCP.git
```

> 📝 **Note**: LMCP isn't on PyPI yet, so we install directly from GitHub. Once published, you'll be able to use `pip install lmcp`.

> 💡 **Why use a virtual environment?** It keeps LMCP and its dependencies separate from your system Python, preventing conflicts.

**Environment ready!** ✅

## 🎯 Step 2: Try It Out (30 seconds)

### Connect to an Existing MCP Server

```python
import asyncio
import lmcp

async def main():
    # Connect to a filesystem server
    async with lmcp.connect("stdio://npx @modelcontextprotocol/server-filesystem ./") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Found {len(tools)} tools!")
        
        # Use a tool
        files = await client.tools.read_directory(path=".")
        print(f"📁 Found {len(files.content)} files in current directory")

# Run it!
asyncio.run(main())
```

Copy this, save as `test.py`, run `python test.py` - done! ✅

## 🛠️ Step 3: Create Your Own Server (1 minute)

```python
import lmcp

@lmcp.server("my-awesome-server")
class MyServer:
    @lmcp.tool("Add two numbers together")
    def add(self, a: int, b: int) -> int:
        """Simply add two numbers."""
        return a + b
    
    @lmcp.tool("Say hello to someone")
    def greet(self, name: str = "World") -> str:
        """Greet someone nicely."""
        return f"Hello, {name}! 👋"
    
    @lmcp.resource("info://server", description="Server information")
    def server_info(self) -> dict:
        """Get server information."""
        return {
            "name": "My Awesome Server",
            "version": "1.0.0",
            "status": "running"
        }

# Run the server
if __name__ == "__main__":
    server = MyServer()
    print("🚀 Starting server...")
    lmcp.run_server(server)
```

Save as `my_server.py`, run `python my_server.py` - your MCP server is live! 🎉

## 🧪 Step 4: Test Your Server (30 seconds)

Open another terminal and test your server:

```bash
# First, activate your environment in the new terminal
source lmcp-env/bin/activate  # Windows: lmcp-env\Scripts\activate

# List tools
lmcp client list-tools stdio://python my_server.py

# Call a tool
lmcp client call-tool stdio://python my_server.py add --args a=5 --args b=3

# Get a resource
lmcp client list-resources stdio://python my_server.py
```

> 🔄 **Remember**: Activate your virtual environment (`source lmcp-env/bin/activate`) in every new terminal!

## 🎨 That's It! You're Ready!

In under 2 minutes, you've:
- ✅ Installed LMCP
- ✅ Connected to an MCP server
- ✅ Created your own MCP server
- ✅ Tested everything with the CLI

## 🔥 Common Patterns (Copy & Paste Ready!)

### Simple Calculator Server
```python
import lmcp
import math

@lmcp.server("calculator")
class Calculator:
    @lmcp.tool("Add numbers")
    def add(self, a: float, b: float) -> float:
        return a + b
    
    @lmcp.tool("Multiply numbers")
    def multiply(self, a: float, b: float) -> float:
        return a * b
    
    @lmcp.tool("Square root")
    def sqrt(self, x: float) -> float:
        return math.sqrt(x)

if __name__ == "__main__":
    lmcp.run_server(Calculator())
```

### File Processing Server
```python
import lmcp
from pathlib import Path

@lmcp.server("file-processor")
class FileProcessor:
    @lmcp.tool("Count lines in file")
    def count_lines(self, filename: str) -> int:
        return len(Path(filename).read_text().splitlines())
    
    @lmcp.tool("Get file size")
    def file_size(self, filename: str) -> int:
        return Path(filename).stat().st_size
    
    @lmcp.resource("files://list", description="List all files")
    def list_files(self) -> list:
        return [str(p) for p in Path(".").glob("*") if p.is_file()]

if __name__ == "__main__":
    lmcp.run_server(FileProcessor())
```

### Simple Client Script
```python
import asyncio
import lmcp

async def use_calculator():
    async with lmcp.connect("stdio://python calculator.py") as calc:
        # Do some math
        result1 = await calc.tools.add(a=10, b=5)
        result2 = await calc.tools.multiply(a=3, b=7)
        result3 = await calc.tools.sqrt(x=16)
        
        print(f"10 + 5 = {result1.content}")
        print(f"3 × 7 = {result2.content}")
        print(f"√16 = {result3.content}")

asyncio.run(use_calculator())
```

## 💡 Pro Tips

1. **Use async context managers** - they handle connections automatically
2. **Type hints are your friend** - LMCP generates schemas from them
3. **Start simple** - add complexity as you need it
4. **Use the CLI for testing** - `lmcp client` commands are super handy
5. **Check examples/** - lots of copy-paste ready code!

## 🆘 Need Help?

### Common Issues & Solutions

**"Command not found: lmcp"**
- Make sure your virtual environment is activated: `source lmcp-env/bin/activate`
- Try reinstalling: `pip install --force-reinstall git+https://github.com/lhassa8/LMCP.git`

**"Could not find a version that satisfies the requirement lmcp"**
- Use the GitHub installation: `pip install git+https://github.com/lhassa8/LMCP.git`
- LMCP isn't on PyPI yet, so `pip install lmcp` won't work

**"Permission denied" or "Access denied"**
- Use a virtual environment instead of system Python
- On Windows: Run terminal as administrator only if needed

**"Module not found" errors**
- Activate your virtual environment in every new terminal
- Check Python version: `python --version` (needs 3.9+)

**Git installation issues**
- Make sure Git is installed: `git --version`
- Alternative: Download the repo as ZIP and use `pip install -e .`

### More Help
- **Examples**: Check the `examples/` folder for more ideas
- **CLI Help**: Run `lmcp --help` for all commands
- **Issues**: Open an issue at https://github.com/lhassa8/LMCP/issues
- **Docs**: Full documentation in README.md

## 🎯 What's Next?

Now that you're up and running:

1. **Browse the examples** in the `examples/` folder
2. **Add middleware** for logging, caching, retries
3. **Create complex servers** with databases, APIs, etc.
4. **Share your server** with others!

**Happy coding!** 🚀