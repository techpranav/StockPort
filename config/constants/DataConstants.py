"""
Data Constants

Constants related to data structure, column names, and data validation.
"""

from config.constants.StringConstants import (
    COLUMN_OPEN,
    COLUMN_HIGH,
    COLUMN_LOW,
    COLUMN_CLOSE,
    COLUMN_VOLUME,
    COLUMN_ADJ_CLOSE
)

# Standard column names (internal representation)
STANDARD_COLUMN_OPEN = 'open'
STANDARD_COLUMN_HIGH = 'high'
STANDARD_COLUMN_LOW = 'low'
STANDARD_COLUMN_CLOSE = 'close'
STANDARD_COLUMN_VOLUME = 'volume'
STANDARD_COLUMN_ADJ_CLOSE = 'adj_close'
STANDARD_COLUMN_DATE = 'date'
STANDARD_COLUMN_TIMESTAMP = 'timestamp'

# Required columns for OHLCV data
REQUIRED_OHLCV_COLUMNS = [
    STANDARD_COLUMN_OPEN,
    STANDARD_COLUMN_HIGH,
    STANDARD_COLUMN_LOW,
    STANDARD_COLUMN_CLOSE,
    STANDARD_COLUMN_VOLUME
]

# Optional columns
OPTIONAL_COLUMNS = [
    STANDARD_COLUMN_ADJ_CLOSE,
    STANDARD_COLUMN_DATE,
    STANDARD_COLUMN_TIMESTAMP
]

# Data validation constants
MIN_DATA_POINTS_FOR_ANALYSIS = 20
MIN_DATA_POINTS_FOR_INDICATORS = 14
MIN_DATA_POINTS_FOR_LONG_INDICATORS = 200

# Data quality thresholds
MAX_MISSING_DATA_PERCENTAGE = 5.0  # 5% missing data allowed
MIN_VOLUME_THRESHOLD = 0  # Minimum volume to consider valid
MAX_PRICE_CHANGE_PERCENT = 50.0  # Maximum single-day price change (sanity check)

# Data type validation
VALID_PRICE_TYPES = ['float64', 'float32', 'int64', 'int32']
VALID_VOLUME_TYPES = ['int64', 'int32', 'float64', 'float32']
VALID_DATE_TYPES = ['datetime64[ns]', 'datetime64']

# Market identifiers
MARKET_US = 'US'
MARKET_NSE = 'NSE'
MARKET_BSE = 'BSE'
MARKET_UNKNOWN = 'UNKNOWN'

# Exchange suffixes for symbol detection
NSE_SUFFIX = '.NS'
BSE_SUFFIX = '.BO'

# Provider names
PROVIDER_YAHOO_FINANCE = 'yahoo_finance'
PROVIDER_ALPHA_VANTAGE = 'alpha_vantage'
PROVIDER_NSE = 'nse'
PROVIDER_BSE = 'bse'
PROVIDER_INVESTPY = 'investpy'

# Default provider
DEFAULT_PROVIDER = PROVIDER_YAHOO_FINANCE

