# How decisions are taken

## Signals vs decisions

- **Signal**: “This looks like a setup” (strategy output)
- **Decision**: “We should place an order” (strategy output + constraints + safety checks)

## What the decision system considers (as implemented)

1. **Signal quality** (score/confidence)
2. **Market regime** (trend/range/volatile)
3. **Capital availability**
4. **Risk limits** (per trade / daily / portfolio)
5. **Data integrity** (provider health, candle validation)
6. **Timing constraints** (staleness, session windows)

## Typical flow (implemented pipeline)

1. **Scanner emits an opportunity** with price/volume + computed indicators.
2. **Strategies evaluate** the opportunity and may emit one or more `StrategySignal` objects.
3. **Decision engine** evaluates a single `StrategySignal` and produces a `TradingDecision`:
   - First rejects **expired** signals (time-based + price-change threshold)
   - Rejects **stale** opportunities (price/volume changed beyond thresholds)
   - Computes **position size** from entry/stop and your configured risk-per-trade
   - Checks the **risk engine** (per-trade risk, daily loss/trade limits, sector exposure, correlation, kill-switch)
   - Rejects if **risk–reward < 1.5:1**
4. **Execution** is permitted only if decision is `APPROVE`.

## Learn more

- If you want a deeper explanation of each stage, start with the **Daily Workflow**: [Daily Workflow](../guides/daily-workflow.md)
- If you are a developer, see the developer documentation “End-to-end flow” page.


