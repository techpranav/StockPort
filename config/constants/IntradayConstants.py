"""
Intraday Trading Constants

This file contains constants specific to intraday and short-term trading analysis.
"""

# Intraday Timeframes
INTRADAY_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h']
SHORT_TERM_TIMEFRAMES = ['1h', '4h', '1d']
ALL_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']

# Market Hours (US Eastern Time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

# Pre-market and After-hours
PRE_MARKET_OPEN_HOUR = 4
PRE_MARKET_OPEN_MINUTE = 0
AFTER_HOURS_CLOSE_HOUR = 20
AFTER_HOURS_CLOSE_MINUTE = 0

# Intraday Indicator Periods
INTRADAY_RSI_PERIOD = 14
INTRADAY_STOCHASTIC_PERIOD = 14
INTRADAY_ADX_PERIOD = 14
INTRADAY_ATR_PERIOD = 14
INTRADAY_CCI_PERIOD = 20

# Short-term Moving Averages
INTRADAY_SMA_FAST = 9
INTRADAY_SMA_SLOW = 21
INTRADAY_EMA_FAST = 12
INTRADAY_EMA_SLOW = 26

# Volume Analysis
INTRADAY_VOLUME_PERIOD = 20
UNUSUAL_VOLUME_MULTIPLIER = 1.5

# Session Boundaries
REGULAR_SESSION = "regular"
PRE_MARKET_SESSION = "pre_market"
AFTER_HOURS_SESSION = "after_hours"

