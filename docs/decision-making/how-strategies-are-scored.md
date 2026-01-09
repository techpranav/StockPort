# How strategies are scored

## Why scoring exists

Multiple strategies can trigger at once. Scoring makes results comparable so the UI and decision engine can prioritize **higher-quality** setups.

## How scoring works

Scoring is a way to rank setups so you can focus on the best ones first.

In general:

- A setup earns points when multiple confirmations line up (trend, momentum, volume, key levels)
- The more confirmations that agree, the higher the score and confidence

## Typical scoring inputs (common across strategies)

- Trend alignment (e.g., SMA/EMA alignment)
- Momentum (RSI zone, MACD bullish)
- Volume confirmation (`volume_ratio`)
- Volatility suitability (ATR%)
- Level/context (support/resistance strength, bounce probability)

## Score vs confidence

- **Score**: how strong the setup looks in the data
- **Confidence**: how likely it is to work given regime/quality/history

## Learn more

If you are a developer, see the developer documentation “Evaluator” page for the exact scoring contract.


