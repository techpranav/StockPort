# Trend following strategy (developer)

## File

`backend/strategies/strategies/trend_following.py`

## Purpose

Detects trend continuation setups with confirmatory filters.

## Entry logic

Conditions from `Opportunity.indicators`:

- Trend: `sma_20 > sma_50` (30 points)
- RSI: `40 <= rsi <= 70` (20 points)
- MACD bullish: `macd > macd_signal` (30 points)
- Pattern (optional): `pattern` contains “bullish” or “engulfing” (20 points)

Enforces:

- `min_confirmations` (default 3)
- `min_score` (default 70)

## Risk proposal (ATR based)

- Stop: `entry - (atr * 2.0)`
- Target: `entry + (atr * 3.0)`


