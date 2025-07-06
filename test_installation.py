#!/usr/bin/env python3
"""
Test LMCP Installation

Quick script to test if LMCP is installed and working correctly.
"""

import sys
from pathlib import Path

# Add the src directory to path so we can import lmcp from local repo
if (Path(__file__).parent / "src").exists():
    sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_import():
    """Test if LMCP can be imported."""
    try:
        import lmcp
        print("✅ LMCP import successful!")
        print(f"📦 Version: {lmcp.__version__}")
        print(f"👤 Author: {lmcp.__author__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import LMCP: {e}")
        return False

def test_basic_functionality():
    """Test basic LMCP functionality."""
    try:
        import lmcp
        
        # Test server creation
        @lmcp.server("test-server")
        class TestServer:
            @lmcp.tool("Test tool")
            def test_tool(self, x: int) -> int:
                return x * 2
        
        server = TestServer()
        tools = server.list_tools()
        
        print(f"✅ Server creation works! Found {len(tools)} tools")
        
        # Test client creation (without actually connecting)
        client = lmcp.connect("stdio://test")
        print("✅ Client creation works!")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_cli():
    """Test if CLI is available."""
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "lmcp", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI is working!")
            print(f"📋 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ CLI test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing LMCP Installation")
    print("=" * 40)
    print()
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Import
    print("🔍 Test 1: Import Test")
    if test_import():
        tests_passed += 1
    print()
    
    # Test 2: Basic functionality
    print("🔍 Test 2: Basic Functionality")
    if test_basic_functionality():
        tests_passed += 1
    print()
    
    # Test 3: CLI
    print("🔍 Test 3: CLI Test")
    if test_cli():
        tests_passed += 1
    print()
    
    # Results
    print("📊 Test Results")
    print("=" * 15)
    print(f"✅ Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! LMCP is ready to use!")
        print()
        print("🚀 Next steps:")
        print("1. Try: lmcp create sample my-test")
        print("2. Run: python my_test_server.py")
        print("3. Test: lmcp client list-tools stdio://python my_test_server.py")
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        print()
        print("💡 Try:")
        print("1. Activate your virtual environment")
        print("2. Reinstall: pip install --force-reinstall git+https://github.com/lhassa8/LMCP.git")
        print("3. Or from repo: pip install -e .")

if __name__ == "__main__":
    main()