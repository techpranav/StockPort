# Mean Reversion Strategy

## What it looks for

**Mean reversion** strategies look for price deviating from an expected “fair” area (often a moving average or a volatility band) and then reverting.

## Regime fit

This strategy is most applicable in **ranging / sideways** regimes.

## Entry conditions (as implemented)

The mean reversion strategy checks (defaults shown):

- **Bollinger/Z-score oversold**: price far below the Bollinger mean (approx z-score < `-2.0`)
- **RSI oversold**: `RSI < 30`
- **Low volatility**: `ATR% < 3.0%`
- **Normal volume**: `0.8 <= volume_ratio <= 1.5`

It requires:

- **Minimum confirmations**: `min_confirmations = 3`
- **Minimum score**: `min_score = 65`

## Scoring model (0–100)

- Bollinger oversold: **40**
- RSI oversold: **30**
- Low volatility: **20**
- Normal volume: **10**

## Stops and targets (as implemented)

- **Entry**: current price
- **Stop-loss**:
  - `bb_lower * 0.99` if Bollinger lower band is present
  - Else **2%** below entry
- **Take-profit**:
  - `bb_middle` (the Bollinger mean) if present
  - Else **2%** above entry

## When it is useful

- Range-bound markets
- Overextended moves where reversal evidence appears

## How to use it

- Prefer setups with **support confirmation** and improving momentum from oversold.
- Avoid fighting strong trends without confirmation.

## Common failure modes

- “Catching a falling knife” in strong downtrends
- News-driven continuation moves

## FAQ

See [Strategies FAQ](../faq/strategies.md).


