# Contributing to LMCP

Thank you for your interest in contributing to LMCP! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - LMCP version
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and stack traces

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Describe the use case** and problem you're solving
3. **Propose a solution** with examples if possible
4. **Consider backwards compatibility**

### Submitting Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow the development setup** instructions below
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Follow code style guidelines**
6. **Submit a pull request** with a clear description

## 🛠️ Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Optional: Docker for testing

### Local Development

```bash
# Clone your fork
git clone https://github.com/lhassa8/LMCP.git
cd LMCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest -m "not slow"        # Skip slow tests

# Run with coverage
pytest --cov=lmcp --cov-report=html
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
ruff .

# Type checking
mypy .

# Run all quality checks
pre-commit run --all-files
```

## 📋 Development Guidelines

### Code Style

- **Follow PEP 8** for Python code style
- **Use Black** for automatic formatting (line length 88)
- **Use isort** for import sorting
- **Use type hints** throughout the codebase
- **Write docstrings** for all public functions and classes

### Testing

- **Write comprehensive tests** for new features
- **Maintain high test coverage** (aim for >90%)
- **Use pytest fixtures** for test setup
- **Mock external dependencies** in unit tests
- **Include integration tests** for end-to-end functionality

### Documentation

- **Update README.md** for user-facing changes
- **Add docstrings** to all public APIs
- **Include examples** in docstrings when helpful
- **Update CHANGELOG.md** for notable changes

### Git Workflow

- **Use descriptive commit messages**
- **Keep commits focused** on a single change
- **Rebase feature branches** before merging
- **Squash related commits** when appropriate

#### Commit Message Format

```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(client): add connection pooling support

Add connection pooling to improve performance when connecting
to multiple MCP servers simultaneously.

Closes #123
```

```
fix(server): handle tool validation errors gracefully

Previously, invalid tool parameters would cause the server to crash.
Now, proper error responses are returned to the client.

Fixes #456
```

## 🏗️ Architecture Guidelines

### Code Organization

```
src/lmcp/
├── __init__.py          # Main API exports
├── client.py            # Client implementation
├── server.py            # Server implementation
├── connection.py        # Connection management
├── types.py             # Type definitions
├── exceptions.py        # Exception classes
├── protocol/            # MCP protocol implementation
├── transports/          # Transport implementations
├── middleware/          # Middleware components
└── utils/               # Utility functions
```

### Design Principles

1. **Simplicity**: Easy to use by default
2. **Flexibility**: Powerful when needed
3. **Type Safety**: Comprehensive type hints
4. **Async First**: Built for modern Python
5. **Extensibility**: Plugin-friendly architecture
6. **Backwards Compatibility**: Semantic versioning

### Adding New Features

#### New Transport

1. Create `src/lmcp/transports/new_transport.py`
2. Inherit from `Transport` base class
3. Implement all abstract methods
4. Add to `__init__.py` exports
5. Write comprehensive tests
6. Add documentation and examples

#### New Middleware

1. Create `src/lmcp/middleware/new_middleware.py`
2. Inherit from `Middleware` base class
3. Implement request/response processing
4. Add configuration options
5. Write unit tests
6. Add usage examples

#### New Tool Decorators

1. Add to `src/lmcp/server.py`
2. Follow existing decorator patterns
3. Support type inference
4. Add validation logic
5. Write tests for edge cases

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                # Unit tests
│   ├── test_client/
│   ├── test_server/
│   ├── test_middleware/
│   └── test_protocol/
├── integration/         # Integration tests
├── conftest.py         # Pytest configuration
└── fixtures/           # Test data and fixtures
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test performance characteristics

### Writing Tests

```python
import pytest
from lmcp import Client, Server

class TestMyFeature:
    """Test the new feature."""
    
    @pytest.mark.asyncio
    async def test_basic_functionality(self):
        """Test basic functionality works."""
        # Arrange
        server = TestServer()
        
        # Act
        result = await server.my_method()
        
        # Assert
        assert result.success
    
    @pytest.mark.integration
    async def test_client_server_integration(self):
        """Test client-server integration."""
        # Integration test implementation
        pass
    
    @pytest.mark.slow
    async def test_performance(self):
        """Test performance characteristics."""
        # Performance test implementation
        pass
```

## 📚 Documentation

### Types of Documentation

1. **API Reference**: Auto-generated from docstrings
2. **User Guide**: Step-by-step tutorials
3. **Examples**: Working code samples
4. **Architecture**: High-level design documentation

### Writing Documentation

- **Use clear, concise language**
- **Include code examples**
- **Test all code examples**
- **Update for breaking changes**
- **Consider different skill levels**

### Docstring Format

```python
def my_function(param1: str, param2: int = 10) -> bool:
    """
    Brief description of the function.
    
    Longer description with more details about what the function
    does, how it works, and any important considerations.
    
    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to 10.
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        ConnectionError: When connection fails
        
    Examples:
        >>> result = my_function("test", 5)
        >>> assert result is True
        
    Note:
        Any additional notes or warnings
    """
```

## 🔄 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Run full test suite**
4. **Update documentation**
5. **Create release tag**
6. **Publish to PyPI**
7. **Create GitHub release**

## 🎯 Areas Needing Contribution

### High Priority

- **Documentation improvements**
- **Test coverage improvements**
- **Performance optimizations**
- **Bug fixes**

### Medium Priority

- **New transport implementations**
- **Additional middleware components**
- **CLI enhancements**
- **Integration examples**

### Low Priority

- **Code style improvements**
- **Type hint improvements**
- **Refactoring opportunities**

## 💬 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Request Reviews**: Code review and feedback

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Getting Help

- **Check the documentation** first
- **Search existing issues** for similar problems
- **Ask questions** in GitHub Discussions
- **Be patient and respectful** when asking for help

## 🙏 Recognition

All contributors will be recognized in our [Contributors](CONTRIBUTORS.md) file. We appreciate all types of contributions, including:

- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions
- Community support
- Testing and feedback

Thank you for contributing to LMCP!