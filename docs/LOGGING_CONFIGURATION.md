# Logging Configuration Guide

**✅ FIXED: DEBUG_MODE Redundancy Removed**
- No more `DEBUG_MODE` flag - the logging system handles everything through `LOG_LEVEL`
- Cleaner, standard Python logging practices
- No double-gating of debug messages

## Quick Reference

### 🔧 Where to Change Log Level

**Primary Location (Permanent Changes):**
```python
# File: config/settings.py
LOG_LEVEL = "DEBUG"  # Change this value
```

**Runtime Changes (Temporary):**
```python
from utils.debug_utils import DebugUtils, LogLevel
DebugUtils.set_log_level(LogLevel.ERROR)  # Change during execution
```

### 📊 Available Log Levels

| Level | Value | What You'll See | Use Case |
|-------|-------|-----------------|----------|
| `"DEBUG"` | 0 | **Everything**: API calls, calculations, data processing, errors | Development, troubleshooting |
| `"INFO"` | 1 | **Status updates**: progress, successful operations, warnings, errors | Production monitoring |
| `"WARNING"` | 2 | **Issues only**: potential problems, missing data, rate limits, errors | Production (quiet) |
| `"ERROR"` | 3 | **Problems only**: exceptions, failures, critical issues | Error monitoring |
| `"CRITICAL"` | 4 | **System failures**: application crashes, critical failures | Emergency monitoring |

### 🎯 Common Scenarios

**Debugging Financial Ratios:**
```python
# config/settings.py
LOG_LEVEL = "DEBUG"  # See all ratio calculations
```

**Production Environment:**
```python
# config/settings.py  
LOG_LEVEL = "INFO"   # Balanced: status + problems
```

**Error Monitoring Only:**
```python
# config/settings.py
LOG_LEVEL = "ERROR"  # Only see problems
```

### 🧪 Testing Configuration

```python
from utils.debug_utils import DebugUtils
DebugUtils.test_logging()  # Shows sample messages at all levels
```

### 📁 Log File Locations

- **Console**: Real-time output during execution
- **File**: `logs/stock_analyzer_YYYYMMDD.log`

### 💡 Pro Tips

1. **Development**: Use `DEBUG` to see everything
2. **Production**: Use `INFO` or `WARNING` 
3. **Troubleshooting**: Temporarily change to `DEBUG` with `DebugUtils.set_log_level()`
4. **Performance**: Higher levels (ERROR, CRITICAL) reduce console noise
5. **File logs**: Always saved regardless of console level

---

*For detailed implementation, see comments in `config/settings.py` and `utils/debug_utils.py`*