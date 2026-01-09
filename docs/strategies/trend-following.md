# Trend Following Strategy

## What it looks for

Trend following aims to participate in **sustained trends**, typically entering on pullbacks or break-and-retest patterns.

## Entry conditions (as implemented)

The trend following strategy checks (defaults shown):

- **Trend filter**: `sma_20 > sma_50`
- **RSI**: `40 <= RSI <= 70`
- **MACD bullish**: `macd > macd_signal`
- **Bullish pattern** (optional): indicator `pattern` contains “bullish” or “engulfing”

It requires:

- **Minimum confirmations**: `min_confirmations = 3`
- **Minimum score**: `min_score = 70`

## Scoring model (0–100)

- SMA20 above SMA50: **30**
- RSI range: **20**
- MACD bullish: **30**
- Bullish pattern: **20** (if detected)

## Stops and targets (as implemented)

Uses ATR-based stops/targets:

- **Entry**: current price
- **Stop-loss**: `entry - (ATR * 2.0)`
- **Take-profit**: `entry + (ATR * 3.0)`

## When it is useful

- Trending markets with stable volatility
- Strong sector or index-led moves

## How to use it

- Prefer signals aligned across timeframes.
- Be cautious when the broader market regime is “risk-off”.

## Common failure modes

- Trend exhaustion reversals
- High-volatility whipsaws

## FAQ

See [Strategies FAQ](../faq/strategies.md).


