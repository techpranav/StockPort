"""
Backtest Constants

Constants for backtesting system configuration.
"""

# Default backtest parameters
DEFAULT_INITIAL_CAPITAL = 100000.0
DEFAULT_POSITION_SIZE_PCT = 10.0
DEFAULT_TRANSACTION_COST = 0.001  # 0.1%

# Stop loss and take profit defaults
DEFAULT_STOP_LOSS_PCT = 5.0
DEFAULT_TAKE_PROFIT_PCT = 10.0

# Performance thresholds
MIN_WIN_RATE = 50.0
MIN_PROFIT_FACTOR = 1.5
MAX_DRAWDOWN_THRESHOLD = 20.0

# Storage
BACKTEST_STORAGE_DIR = "backtests"
MAX_BACKTEST_HISTORY = 1000

