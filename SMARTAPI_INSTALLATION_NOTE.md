# SmartApi Installation Note

## ✅ RESOLVED

SmartApi (version 1.1.0) is now properly integrated using `pycryptodome` as a drop-in replacement for PyCrypto.

## Installation

```bash
# Install SmartApi WITHOUT dependencies to avoid PyCrypto issues
pip install SmartApi --no-deps

# Then install pycryptodome separately (drop-in replacement for PyCrypto)
pip install pycryptodome>=3.23.0
```

## Important Notes

1. **DO NOT install PyCrypto** - We use `pycryptodome` instead
2. **Import SmartConnect correctly** - Always use `from broker import SmartConnect` (never import directly from SmartApi)
3. **Ignore pip warnings** - Pip may warn about PyCrypto dependency conflicts, but runtime imports are correct

## Import Rules

### ❌ WRONG:
```python
from SmartApi import SmartConnect  # This will FAIL
from smartapi import SmartConnect  # This is also WRONG
```

### ✅ CORRECT:
```python
from broker import SmartConnect  # Always use this
# OR
from broker.angelone import SmartConnect
```

## Verification

To verify installation:
```bash
python -m broker.verification
```

## Documentation

See [SmartAPI Integration Guide](docs/dev/SMARTAPI_INTEGRATION.md) for complete details.
