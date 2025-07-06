# 📦 Publishing LMCP to PyPI

When you're ready to publish LMCP to PyPI so users can install with `pip install lmcp`, follow these steps:

## 🎯 Prerequisites

1. **Create PyPI account**: Go to https://pypi.org and create an account
2. **Install build tools**:
   ```bash
   pip install build twine
   ```

## 🔧 One-Time Setup

1. **Create API token** on PyPI:
   - Go to https://pypi.org/manage/account/
   - Scroll to "API tokens" 
   - Click "Add API token"
   - Name it "LMCP" and select "Entire account"
   - Copy the token (starts with `pypi-`)

2. **Configure credentials**:
   ```bash
   # Create ~/.pypirc file
   cat > ~/.pypirc << 'EOF'
   [distutils]
   index-servers = pypi

   [pypi]
   username = __token__
   password = pypi-YOUR_TOKEN_HERE
   EOF
   ```

## 🚀 Publishing Steps

### 1. Test Everything Locally First
```bash
# Run all tests
python test_installation.py
pytest

# Test package building
python -m build
```

### 2. Update Version (if needed)
Edit `pyproject.toml`:
```toml
version = "0.1.0"  # Increment this for new releases
```

### 3. Build the Package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build
python -m build
```

This creates:
- `dist/lmcp-0.1.0.tar.gz` (source distribution)
- `dist/lmcp-0.1.0-py3-none-any.whl` (wheel)

### 4. Test Upload (Optional - Test PyPI)
```bash
# Upload to test PyPI first
twine upload --repository testpypi dist/*

# Test install from test PyPI
pip install --index-url https://test.pypi.org/simple/ lmcp
```

### 5. Real Upload to PyPI
```bash
# Upload to real PyPI
twine upload dist/*
```

### 6. Test Installation
```bash
# Test that users can now install
pip install lmcp
```

## 🎉 After Publishing

1. **Update documentation** - Change installation instructions from GitHub to PyPI
2. **Create GitHub release** - Tag the version and create release notes
3. **Announce** - Share with the community!

## 🔄 For Future Updates

1. **Update version** in `pyproject.toml`
2. **Build and upload**:
   ```bash
   rm -rf dist/
   python -m build
   twine upload dist/*
   ```

## 🆘 Troubleshooting

**"Package already exists"**
- Increment version number in `pyproject.toml`
- You can't overwrite existing versions

**"Invalid credentials"**
- Check your API token in `~/.pypirc`
- Make sure token starts with `pypi-`

**"Upload failed"**
- Check package name isn't taken: https://pypi.org/project/lmcp/
- Try a different name if "lmcp" is taken

## 📋 Checklist Before Publishing

- [ ] All tests pass (`pytest`)
- [ ] Installation test works (`python test_installation.py`) 
- [ ] Examples work (`python get_started.py`)
- [ ] Version number updated
- [ ] README.md is accurate
- [ ] License file included
- [ ] GitHub repo is public and up-to-date

## 💡 Pro Tips

1. **Start with test PyPI** - Always test there first
2. **Use semantic versioning** - 0.1.0, 0.1.1, 0.2.0, etc.
3. **Write good release notes** - Help users understand changes
4. **Keep dependencies minimal** - Only include what's necessary

---

**Don't rush!** Test everything locally first. PyPI publishing is permanent - you can't delete versions once uploaded.