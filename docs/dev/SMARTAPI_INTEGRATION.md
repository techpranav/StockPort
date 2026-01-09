# SmartAPI Integration Guide

## Overview

Stockport uses **Angel One SmartAPI** (SmartApi version 1.1.0) for broker integration and live market data. This document explains the correct way to import and use SmartAPI in the codebase.

## Installation

SmartApi is already installed in the virtual environment. If you need to reinstall:

```bash
# Install SmartApi WITHOUT dependencies to avoid PyCrypto issues
pip install SmartApi --no-deps

# Then install pycryptodome separately (drop-in replacement for PyCrypto)
pip install pycryptodome>=3.23.0
```

**Important**: Do NOT install PyCrypto. We use `pycryptodome` as a drop-in replacement.

## Import Rules

### ❌ WRONG - Do NOT use this:

```python
from SmartApi import SmartConnect  # This will FAIL
```

### ✅ CORRECT - Always use this:

```python
from broker.angelone import SmartConnect
# OR
from broker import SmartConnect
```

## Why This Architecture?

1. **Single Import Point**: `broker/angelone.py` is the ONLY place where SmartApi is directly imported
2. **Correct Import Path**: SmartConnect must be imported from `SmartApi.smartConnect`, not `SmartApi`
3. **Dependency Management**: We use `pycryptodome` instead of `PyCrypto` to avoid C++ build tool requirements
4. **Future-Proof**: If SmartApi changes, we only need to update one file

## Verification

To verify SmartAPI installation:

```python
from broker.verification import verify_smartapi_installation

success, message = verify_smartapi_installation()
if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

Or run directly:

```bash
python -m broker.verification
```

## Python Version Compatibility

- **Tested on**: Python 3.10+ and Python 3.14
- **Platform**: Windows (primary), Linux/Mac (should work)
- **Dependencies**: pycryptodome (not PyCrypto)

## Common Issues

### Issue: ImportError when importing SmartConnect

**Solution**: Ensure you're importing from `broker.angelone`, not directly from SmartApi.

### Issue: PyCrypto dependency warnings

**Solution**: Ignore pip warnings about PyCrypto. We use `pycryptodome` at runtime, which is a drop-in replacement.

### Issue: SmartApi installation fails

**Solution**: Install with `--no-deps` flag:
```bash
pip install SmartApi --no-deps
pip install pycryptodome
```

## Code Examples

### Basic Usage

```python
from broker import SmartConnect
from config.app_config import get_angel_credentials

# Get credentials
api_key, client_id, password = get_angel_credentials()

# Create SmartConnect instance
smart_connect = SmartConnect(api_key)

# Login
data = smart_connect.generateSession(client_id, password)
```

### In Data Providers

```python
# backend/data/providers/broker/angel_smartapi_provider.py
from broker import SmartConnect

class AngelSmartAPIDataProvider:
    def __init__(self, api_key: str, client_id: str, password: str):
        self.smart_connect = SmartConnect(api_key)
        # ... rest of implementation
```

## Files Structure

```
broker/
├── __init__.py          # Exports SmartConnect
├── angelone.py          # ONLY direct SmartApi import point
└── verification.py      # Installation verification helper
```

## Developer Notes

- **Never import SmartApi directly** outside of `broker/angelone.py`
- **Always use `broker.angelone`** or `broker` for SmartConnect imports
- **PyCrypto is NOT installed** - we use pycryptodome
- **Ignore pip warnings** about PyCrypto dependency conflicts

## Related Documentation

- [Angel SmartAPI Setup Guide](ANGEL_SMARTAPI_SETUP.md)
- [Data Providers Architecture](DATA_PROVIDERS.md)

