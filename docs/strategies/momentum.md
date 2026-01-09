# Momentum Strategy

## What it looks for

Momentum strategies look for **persistent directional strength**, often combining trend direction, recent returns, and volume confirmation.

## Entry conditions (as implemented)

The momentum strategy checks (defaults shown):

- **Rate of Change (ROC)**: `roc > 0.05` (5% momentum)
- **Volume spike**: `volume_ratio > 1.2` (20% above average)
- **RSI momentum zone**: `50 <= RSI <= 70`

It requires:

- **Minimum confirmations**: `min_confirmations = 2`
- **Minimum score**: `min_score = 60`

## Scoring model (0–100)

- ROC: **40**
- Volume spike: **30**
- RSI momentum zone: **30**

## Stops and targets (as implemented)

Uses ATR-based stops/targets:

- **Entry**: current price
- **Stop-loss**: `entry - (ATR * 1.5)`
- **Take-profit**: `entry + (ATR * 2.5)`

## When it is useful

- Strong trending markets
- Post-breakout continuation

## How to use it

- Prefer signals aligned with higher-timeframe trend.
- Be cautious of late-stage momentum (overextension).

## Common failure modes

- Reversals after extended runs
- Low-liquidity spikes

## FAQ

See [Strategies FAQ](../faq/strategies.md).


