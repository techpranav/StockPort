# Momentum strategy (developer)

## File

`backend/strategies/strategies/momentum.py`

## Purpose

Detects directional momentum setups and emits signals for continuation opportunities.

## Entry logic

Builds conditions from `Opportunity.indicators`:

- ROC: `roc > 0.05` (40 points)
- Volume: `volume_ratio > 1.2` (30 points)
- RSI: `50 <= rsi <= 70` (30 points)

Enforces:

- `min_confirmations` (default 2)
- `min_score` (default 60)

## Risk proposal (ATR based)

- Stop: `entry - (atr * 1.5)`
- Target: `entry + (atr * 2.5)`


