# Swing trading strategy (developer)

## File

`backend/strategies/strategies/swing_trading.py`

## Purpose

Detects multi-day swing setups (trend + pullback/resumption).

## Entry logic

Uses `Opportunity.indicators`:

- EMA alignment: `ema_20 > ema_50 > sma_200` (30 points)
- MACD bullish: `macd > macd_signal` (25 points)
- RSI: `40 <= rsi <= 70` (20 points)
- Volume: `volume_ratio > 1.1` (15 points)
- Support context: `current_price > nearest_support * 1.02` (10 points, optional)

Enforces:

- `min_confirmations` (default 4)
- `min_score` (default 75)

## Risk proposal

- Stop: below EMA20 (or 3% below entry)
- Target: `entry * 1.06` (default 6%)


