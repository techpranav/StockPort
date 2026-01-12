# Numeric Constants
# This file contains all numeric constants used throughout the application

# Technical Analysis Periods and Windows
SMA_SHORT_PERIOD = 20
SMA_LONG_PERIOD = 50
RSI_PERIOD = 14
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
BOLLINGER_PERIOD = 20
BOLLINGER_STD_DEV = 2
MIN_DATA_POINTS_FOR_ANALYSIS = 20

# RSI Thresholds
RSI_OVERBOUGHT_THRESHOLD = 70
RSI_OVERSOLD_THRESHOLD = 30
RSI_NEUTRAL_VALUE = 50

# Volatility Thresholds (percentage)
HIGH_VOLATILITY_THRESHOLD = 3.0
LOW_VOLATILITY_THRESHOLD = 1.0

# Volume Analysis Multipliers
HIGH_VOLUME_MULTIPLIER = 1.5
LOW_VOLUME_MULTIPLIER = 0.5

# API Related Constants
DELAY_BETWEEN_CALLS = 60  # seconds
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
API_RATE_LIMIT_DELAY = 10  # seconds
API_MAX_RETRIES = 3
API_REQUEST_DELAY = 2  # seconds
API_RATE_LIMIT_COOLDOWN = 120  # seconds

# Default Values
DEFAULT_LIMIT = 5
DEFAULT_DAYS_BACK = 365
DEFAULT_NEWS_LIMIT = 5

# Import from StringConstants to avoid duplication
from .StringConstants import DEFAULT_PERIOD

# File Size and Cleanup
DEFAULT_CLEANUP_DAYS = 30
MAX_FILE_SIZE_MB = 100

# Chart and Display Settings
CHART_WIDTH = 800
CHART_HEIGHT = 400
MAX_CHART_POINTS = 1000

# Financial Analysis Thresholds
GOOD_CURRENT_RATIO = 2.0
MINIMUM_CURRENT_RATIO = 1.0
HIGH_DEBT_TO_EQUITY = 2.0
GOOD_ROE_THRESHOLD = 15.0  # percentage
GOOD_ROA_THRESHOLD = 5.0   # percentage