# Mean reversion strategy (developer)

## File

`backend/strategies/strategies/mean_reversion.py`

## Purpose

Detects overextension and potential reversion-to-mean setups.

## Inputs required

- `Opportunity.indicators` should include (or the strategy will use fallbacks):
  - `bb_upper`, `bb_lower`, `bb_middle`
  - `rsi`, `atr`, `volume_ratio`

## Entry logic

- Approximate Bollinger z-score using band width:
  - marks oversold when z-score < `-z_score_threshold` (default 2.0)
- Confirms RSI oversold: `rsi < rsi_oversold` (default 30)
- Prefers low volatility: `atr_pct < 3.0`
- Prefers normal volume: `0.8 <= volume_ratio <= 1.5`

Enforces:

- `min_confirmations` (default 3)
- `min_score` (default 65)

## Risk proposal

- Entry: current price
- Stop: `bb_lower * 0.99` else `entry * 0.98`
- Target: `bb_middle` else `entry * 1.02`


