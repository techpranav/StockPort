# Scanner

## What it does

The **Scanner** continuously watches a symbol universe and produces **opportunities** (candidate stocks worth evaluating) based on basic liquidity/quality filters and indicator calculations.

In Stockport terms:

- **Opportunity**: output of scanning (symbol + price/volume + indicators)
- **Signal**: output of a strategy evaluating an opportunity

## What you see in the UI

- **Opportunity stream**: New candidates as they appear.
- **Filters**: Narrow by symbol, strategy, confidence, regime, and freshness.
- **Explainability**: “Why this appeared” highlights the main drivers.

## Pre-filters (what gets filtered out early)

To avoid noisy/untradeable symbols, the scanner applies pre-filters (loaded from settings):

- Minimum price
- Minimum volume
- Minimum market cap

If a symbol fails these, it never reaches strategy evaluation.

## Indicators (what gets calculated)

Strategies rely on indicators like SMA/EMA, RSI, MACD, ATR, volume ratios, and (for some strategies) Bollinger bands and support/resistance context.

!!! note
    Some strategy indicators require richer history or provider-specific calculations. If you notice a strategy never triggering, verify indicator availability and provider health.

## How to use it (recommended flow)

1. Start in **Discover** workspace and watch the opportunity stream.
2. Filter to your preferred **timeframe** and **strategy style** (breakout / mean reversion / trend).
3. Open the top candidates in **Decide** to evaluate risk–reward and constraints.
4. If approved, move to **Execute** to place/monitor the order.

## Common issues

- **No opportunities**: Data provider may be unhealthy, or filters are too strict.
- **Too many opportunities**: Use regime/confidence filters and reduce the symbol universe.

## FAQ

See [General FAQ](../faq/general.md) and [Data Providers FAQ](../faq/data-providers.md).


