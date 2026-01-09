# Breakout Strategy

## What it looks for

A **breakout** aims to catch price moving beyond an important level (typically resistance), ideally with expanding volume and follow-through.

## Regime fit

This strategy is most applicable in **uptrending / bullish** regimes.

## Entry conditions (as implemented)

The breakout strategy checks (defaults shown):

- **Resistance breakout**: current price is **> 1% above** a validated resistance level
- **Volume confirmation**: `volume_ratio >= 1.5` (50% above average)
- **ATR expansion**: `ATR% > 2.0%` (proxy for increased volatility)
- **Momentum confirmation**: `RSI` between **50 and 70**

It requires:

- **Minimum confirmations**: `min_confirmations = 3`
- **Minimum score**: `min_score = 70`

!!! note
    Breakout requires **historical data** to compute and validate support/resistance levels.

## Scoring model (0–100)

- Resistance breakout: **40**
- Volume spike: **30**
- ATR expansion: **15**
- RSI momentum zone: **15**

The final score is a sum of met conditions.

## Stops and targets (as implemented)

- **Entry**: current price
- **Stop-loss**: 1% below the broken resistance level (`stop = resistance * 0.99`)
- **Take-profit**:
  - Next resistance above entry if available
  - Otherwise default to **5%** above entry

## When it is useful

- Trending or transitioning markets
- Consolidation → expansion phases

## How to use it

- Prefer breakouts with **clean structure** (clear range/level).
- Treat low-volume breakouts as lower confidence.

## Common failure modes

- False breakouts (“bull traps”)
- Breakouts into strong higher-timeframe resistance

## FAQ

See [Strategies FAQ](../faq/strategies.md).


