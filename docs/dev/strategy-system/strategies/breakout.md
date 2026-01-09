# Breakout strategy (developer)

## File

`backend/strategies/strategies/breakout.py`

## Purpose

Detects breakout-style setups and emits signals with explainability fields.

## Dependencies

- Support/resistance calculation and validation:
  - `services/analyzers/indicators/support_resistance.py`
  - `services/analyzers/indicators/support_resistance_validator.py`

## Inputs required

- `Opportunity` with (at least) `price` and `indicators`:
  - `volume_ratio`, `atr`, `rsi`
- `historical_data` DataFrame (required) to compute validated levels

## Entry logic (key details)

- Compute current support/resistance levels from history
- Identify a **broken resistance**: `current_price > resistance_level * 1.01`
- Build conditions:
  - resistance breakout (40 points)
  - volume spike `volume_ratio >= min_volume_spike` (30 points)
  - ATR% > 2.0 (15 points)
  - RSI between 50 and 70 (15 points)
- Enforce `min_confirmations` (default: 3) and `min_score` (default: 70)

## Risk proposal

- Entry: current price
- Stop: `broken_resistance_level * 0.99`
- Target: next resistance above entry, else `entry * 1.05`

## How to extend

- Add/modify indicators/pattern checks inside the strategy evaluation
- Keep outputs compatible with the evaluator’s expected schema


