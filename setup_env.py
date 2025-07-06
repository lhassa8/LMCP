#!/usr/bin/env python3
"""
LMCP Environment Setup Script

Automatically sets up a Python virtual environment for LMCP development.
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
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def main():
    """Set up the LMCP development environment."""
    print("🚀 LMCP Environment Setup")
    print("=" * 40)
    print()
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 9):
        print(f"❌ Python 3.9+ required. You have {python_version.major}.{python_version.minor}")
        print("Please upgrade Python and try again.")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Determine the current directory
    current_dir = Path.cwd()
    env_dir = current_dir / "lmcp-env"
    
    print(f"📁 Setting up environment in: {env_dir}")
    print()
    
    # Create virtual environment
    if not run_command(f"python -m venv {env_dir}", "Creating virtual environment"):
        sys.exit(1)
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = env_dir / "Scripts" / "activate.bat"
        pip_cmd = str(env_dir / "Scripts" / "pip")
        activation_cmd = f"{env_dir}\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_script = env_dir / "bin" / "activate"
        pip_cmd = str(env_dir / "bin" / "pip")
        activation_cmd = f"source {env_dir}/bin/activate"
    
    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, but continuing...")
    
    # Install LMCP in development mode if we're in the repo
    pyproject_path = current_dir / "pyproject.toml"
    if pyproject_path.exists():
        print("📦 Found pyproject.toml - installing LMCP in development mode...")
        if run_command(f"{pip_cmd} install -e .[dev]", "Installing LMCP (development mode)"):
            print("✅ LMCP installed in development mode!")
        else:
            print("❌ Development install failed. Try manual installation.")
    else:
        print("📦 Installing LMCP from GitHub...")
        if run_command(f"{pip_cmd} install git+https://github.com/lhassa8/LMCP.git", "Installing LMCP from GitHub"):
            print("✅ LMCP installed successfully!")
        else:
            print("❌ Installation failed. Please check your internet connection and Git installation.")
            print("💡 Alternative: Clone the repo and run 'pip install -e .'")
            sys.exit(1)
    
    print()
    print("🎉 Environment setup complete!")
    print("=" * 40)
    print()
    print("📋 Next steps:")
    print(f"1. Activate the environment: {activation_cmd}")
    print("2. Test the installation: lmcp --version")
    print("3. Create your first server: lmcp create sample my-server")
    print("4. Run it: python my_server_server.py")
    print()
    print("💡 Remember to activate the environment in every new terminal!")
    print()
    
    # Create a simple activation reminder
    reminder_file = current_dir / "activate_env.txt"
    reminder_content = f"""
# LMCP Environment Activation

To activate your LMCP environment, run:

{activation_cmd}

Then you can use:
- lmcp --help
- lmcp create sample my-server
- python my_server_server.py

Remember to activate the environment in every new terminal!
"""
    
    reminder_file.write_text(reminder_content.strip())
    print(f"📝 Activation reminder saved to: {reminder_file}")
    print()
    print("🚀 Happy coding with LMCP!")


if __name__ == "__main__":
    main()