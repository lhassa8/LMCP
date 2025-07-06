#!/usr/bin/env python3
"""
Local LMCP Installation Script

Sets up LMCP for development/testing from the local repository.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed!")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False


def main():
    """Set up LMCP locally."""
    print("🏠 LMCP Local Installation")
    print("=" * 40)
    print()
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    pyproject_path = current_dir / "pyproject.toml"
    
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found!")
        print("Please run this script from the LMCP repository root directory.")
        sys.exit(1)
    
    print(f"📁 Working directory: {current_dir}")
    print(f"✅ Found pyproject.toml")
    print()
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 9):
        print(f"❌ Python 3.9+ required. You have {python_version.major}.{python_version.minor}")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    print()
    
    # Create virtual environment
    env_dir = current_dir / "lmcp-env"
    
    if env_dir.exists():
        print(f"📁 Virtual environment already exists: {env_dir}")
        response = input("🤔 Remove and recreate? (y/N): ").lower().strip()
        if response == 'y':
            import shutil
            shutil.rmtree(env_dir)
            print("🗑️  Removed existing environment")
        else:
            print("👍 Using existing environment")
    
    if not env_dir.exists():
        if not run_command(f"python3 -m venv {env_dir}", "Creating virtual environment"):
            sys.exit(1)
    
    # Determine activation script and commands based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = str(env_dir / "Scripts" / "pip")
        python_cmd = str(env_dir / "Scripts" / "python")
        activation_cmd = f"{env_dir}\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        pip_cmd = str(env_dir / "bin" / "pip")
        python_cmd = str(env_dir / "bin" / "python")
        activation_cmd = f"source {env_dir}/bin/activate"
    
    # Upgrade pip
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install LMCP in development mode
    if not run_command(f"{pip_cmd} install -e .[dev]", "Installing LMCP in development mode"):
        print("❌ Failed to install LMCP")
        sys.exit(1)
    
    print()
    print("🎉 Installation complete!")
    print("=" * 30)
    print()
    print("📋 What was installed:")
    print("✅ LMCP in development mode")
    print("✅ All development dependencies")
    print("✅ CLI tools (lmcp command)")
    print()
    print("🚀 Test your installation:")
    print(f"1. Activate environment: {activation_cmd}")
    print("2. Test CLI: lmcp --version")
    print("3. Run demo: python get_started.py")
    print("4. Run tests: python test_installation.py")
    print()
    print("💡 Next steps:")
    print("• Create a server: lmcp create sample my-server")
    print("• Run it: python my_server_server.py")
    print("• Test it: lmcp client list-tools stdio://python my_server_server.py")
    print()
    
    # Create activation reminder
    reminder_content = f"""
# LMCP Development Environment

To activate your development environment:
{activation_cmd}

Quick commands:
• lmcp --help                    # Show all CLI commands
• lmcp create sample my-server   # Create a sample server
• python get_started.py         # Run the demo
• python test_installation.py   # Test installation
• pytest                        # Run tests

Repository: {current_dir}
Environment: {env_dir}
"""
    
    reminder_file = current_dir / "DEV_ENVIRONMENT.txt"
    reminder_file.write_text(reminder_content.strip())
    print(f"📝 Development guide saved: {reminder_file}")
    print()
    print("🎯 Happy coding with LMCP!")


if __name__ == "__main__":
    main()