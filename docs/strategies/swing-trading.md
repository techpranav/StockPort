# Swing Trading Strategy

## What it looks for

Swing trading in Stockport focuses on capturing **multi-day moves** with entries based on trend structure and pullback/resumption behavior.

## Regime fit

This strategy is most applicable in **trending** regimes (both bullish and bearish contexts).

## Entry conditions (as implemented)

The swing trading strategy checks (defaults shown):

- **Trend alignment**: `ema_20 > ema_50 > sma_200`
- **MACD bullish**: `macd > macd_signal`
- **RSI**: `40 <= RSI <= 70` (momentum without extreme overbought)
- **Volume**: `volume_ratio > 1.1`
- **Above support context** (optional): current price > nearest support by ~2%

It requires:

- **Minimum confirmations**: `min_confirmations = 4`
- **Minimum score**: `min_score = 75`

## Scoring model (0–100)

- EMA alignment: **30**
- MACD bullish: **25**
- RSI range: **20**
- Volume above average: **15**
- Above support: **10**

## Stops and targets (as implemented)

- **Entry**: current price
- **Stop-loss**: below EMA20 with a buffer (or 3% below entry, whichever is tighter)
- **Take-profit**: ~**6%** above entry (default)

## When it is useful

- Clear higher-timeframe trends
- Clean pullbacks to support or key averages

## How to use it

- Use wider stops than intraday strategies (volatility-aware).
- Prefer signals with strong structure (higher highs / higher lows).

## Common failure modes

- Sideways chop (no follow-through)
- Gaps against the position

## FAQ

See [Strategies FAQ](../faq/strategies.md).


