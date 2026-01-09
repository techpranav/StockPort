# Support/Resistance Bounce Strategy

## What it looks for

This strategy looks for price **respecting a key level** (support/resistance) and bouncing with confirmation (e.g., rejection wicks, improving momentum, or volume changes).

## Entry conditions (as implemented)

This strategy requires **historical data** to compute and validate support/resistance.

It checks (defaults shown):

- **Near support**: price is near a validated support level
- **Support strength**: `support_strength >= 60`
- **Bounce probability**: `bounce_probability >= 0.6` (60%)
- **Volume confirmation** (optional): `volume_ratio > 1.2`
- **RSI oversold confirmation** (optional): `RSI < 40`

It requires:

- **Minimum confirmations**: `min_confirmations = 3`
- **Minimum score**: `min_score = 65`

## Scoring model (0–100)

- Near strong support: up to **40** (derived from support strength)
- High bounce probability: up to **30** (derived from bounce probability)
- Volume spike: **20** (if met)
- RSI oversold: **10** (if met)

## Stops and targets (as implemented)

- **Entry**: `support_level * 1.005` (0.5% buffer above support)
- **Stop-loss**: `support_level * 0.99` (1% below support)
- **Take-profit**:
  - Nearest validated resistance if available
  - Else defaults to **5%** above entry

## When it is useful

- Ranges
- Pullbacks in trends where the level has clear historical significance

## How to use it

- Prefer levels that were tested multiple times.
- Confirm with rejection evidence before entry.

## Common failure modes

- Level breaks due to regime change
- “Bounces” that lack follow-through volume

## FAQ

See [Strategies FAQ](../faq/strategies.md).


