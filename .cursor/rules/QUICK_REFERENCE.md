# Stock Analysis Project - Quick Reference Guide

## File Locations

### Constants
- **Numeric values**: `config/constants/NumericConstants.py`
- **String values**: `config/constants/StringConstants.py`
- **User messages**: `config/constants/Messages.py`
- **Financial thresholds**: `config/constants/FinancialConstants.py`
- **Intraday settings**: `config/constants/IntradayConstants.py`

### Configuration
- **All settings**: `config/app_config.py` (single source of truth)
- **Environment variables**: Load via `os.getenv()` in `app_config.py`

### Code Organization
- **Business logic**: `services/` (analyzers, data_providers, exporters)
- **Core orchestration**: `core/` (stock_analyzer, parallel_analyzer)
- **Data models**: `models/` (stock_data, signals, risk_metrics)
- **UI components**: `ui/components/` and `ui/pages/`
- **Utilities**: `utils/` (debug_utils, file_utils, cache_manager)
- **Exceptions**: `exceptions/` (stock_data_exceptions)

## Common Patterns

### Adding a New Indicator
```python
# 1. Add constant to NumericConstants.py
INDICATOR_PERIOD = 14

# 2. Create function in services/analyzers/indicators/
def calculate_new_indicator(data: pd.DataFrame) -> pd.Series:
    """Calculate new indicator."""
    # Implementation
    pass

# 3. Add to TechnicalAnalyzer.calculate_indicators()
```

### Adding a New Constant
```python
# In config/constants/NumericConstants.py (for numbers)
NEW_THRESHOLD = 70

# In config/constants/StringConstants.py (for strings)
NEW_LABEL = "New Label"

# Import where needed
from config.constants.NumericConstants import NEW_THRESHOLD
```

### Adding a New Service
```python
# In services/analyzers/
class NewAnalyzer:
    """Analyzer for new functionality."""
    
    def __init__(self):
        """Initialize analyzer."""
        pass
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform analysis."""
        pass
```

### Error Handling Template
```python
from exceptions.stock_data_exceptions import DataProcessingException
from utils.debug_utils import DebugUtils

def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Process data with error handling."""
    try:
        # Validate input
        if data.empty:
            raise DataProcessingException("Data cannot be empty")
        
        # Process
        result = perform_processing(data)
        return result
        
    except DataProcessingException:
        raise  # Re-raise custom exceptions
    except Exception as e:
        DebugUtils.log_error(e, "Error processing data")
        raise DataProcessingException(f"Processing failed: {e}") from e
```

### Logging Template
```python
from utils.debug_utils import DebugUtils

# Info for normal operations
DebugUtils.info(f"Processing stock: {symbol}")

# Warning for potential issues
DebugUtils.warning(f"Low volume for {symbol}")

# Error for failures
DebugUtils.error(f"Failed to fetch {symbol}")

# Debug for troubleshooting
DebugUtils.debug(f"RSI value: {rsi}")

# Exception logging
try:
    process()
except Exception as e:
    DebugUtils.log_error(e, f"Error in {function_name}")
```

### Type Hints Template
```python
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd

# Simple function
def calculate_rsi(prices: pd.Series) -> pd.Series:
    pass

# With optional return
def get_price(symbol: str) -> Optional[float]:
    pass

# With multiple types
def process(data: Union[pd.DataFrame, Dict]) -> pd.DataFrame:
    pass

# Complex return
def analyze() -> Tuple[pd.DataFrame, Dict[str, float]]:
    pass
```

### Docstring Template
```python
def calculate_indicator(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculate indicator name.
    
    Brief description of what the indicator measures and its purpose.
    
    Args:
        data: DataFrame containing OHLCV data
        window: Period for calculation (default: 14)
        
    Returns:
        Series containing indicator values
        
    Raises:
        DataProcessingException: If data is invalid or calculation fails
        
    Example:
        >>> data = pd.DataFrame({'Close': [100, 102, 101]})
        >>> result = calculate_indicator(data)
        >>> result.iloc[-1]
        50.5
    """
    pass
```

## Naming Conventions Quick Reference

| Type | Convention | Example |
|------|-----------|---------|
| Files/Modules | `snake_case` | `stock_analyzer.py` |
| Classes | `PascalCase` | `StockAnalyzer` |
| Functions/Methods | `snake_case` | `calculate_rsi()` |
| Variables | `snake_case` | `current_price` |
| Constants | `UPPER_SNAKE_CASE` | `RSI_OVERBOUGHT_THRESHOLD` |
| Private methods | `_snake_case` | `_calculate_internal()` |

## Import Order

```python
# 1. Standard library
import os
from typing import Dict, List
from datetime import datetime

# 2. Third-party
import pandas as pd
import numpy as np
from streamlit import st

# 3. Local application
from config.constants.NumericConstants import RSI_PERIOD
from services.analyzers.technical_analysis import TechnicalAnalyzer
from utils.debug_utils import DebugUtils
```

## Common Mistakes to Avoid

1. ❌ Using `print()` instead of `DebugUtils`
2. ❌ Hardcoding values instead of constants
3. ❌ Using relative imports (`from ..module`)
4. ❌ Missing type hints on functions
5. ❌ Missing docstrings on public functions
6. ❌ Bare `except:` clauses
7. ❌ Committing secrets/API keys
8. ❌ Using magic numbers
9. ❌ Breaking existing APIs without migration
10. ❌ Not validating input data

## Quick Checklist

Before committing code:

- [ ] Type hints on all functions
- [ ] Docstrings on public functions/classes
- [ ] Constants in appropriate files
- [ ] No `print()` statements
- [ ] Proper error handling
- [ ] Absolute imports only
- [ ] Follows PEP 8
- [ ] No secrets in code
- [ ] Appropriate logging
- [ ] Tests added/updated

