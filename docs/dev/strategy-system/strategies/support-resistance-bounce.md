# Support/resistance bounce strategy (developer)

## File

`backend/strategies/strategies/support_resistance_bounce.py`

## Purpose

Detects bounces off important support/resistance levels with confirmation.

## Inputs required

- `historical_data` DataFrame is required to compute levels
- `Opportunity.indicators` should include:
  - `volume_ratio`, `rsi`

## Entry logic

- Compute and validate support/resistance levels from history
- Require `near_support` to exist
- Hard gates:
  - `support_strength >= min_support_strength` (default 60)
  - `bounce_probability >= min_bounce_probability` (default 0.6)
- Scoring:
  - support strength scaled up to 40 points
  - bounce probability scaled up to 30 points
  - volume spike adds 20 points
  - RSI oversold adds 10 points

## Risk proposal

- Entry: `support_level * 1.005`
- Stop: `support_level * 0.99`
- Target: nearest resistance if available, else default 5% target


