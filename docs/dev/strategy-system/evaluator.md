# Evaluator

This page explains how Stockport runs strategies and aggregates their outputs.

## Implementation file

`backend/strategies/evaluator.py`

## Responsibilities (high level)

- Runs a set of strategies for a symbol universe
- Collects raw signals/opportunities
- Normalizes/compares them using a common scoring model
- Produces ranked candidates for downstream decision + execution

## How evaluation works (as implemented)

### Active strategies only

The evaluator requests `strategy_registry.get_active()` and ignores paused/disabled strategies.

### Market state is optional

If a `MarketStateEngine` is provided and `market_state` is not passed in, the evaluator pulls:

- `regime`
- `volatility_state`
- `breadth_state`

### Historical data support is dynamic

Some strategies need history (e.g., support/resistance). The evaluator uses runtime inspection:

- If the strategy `evaluate()` signature contains `historical_data`, it passes it.
- Otherwise, it calls the two-arg form.

### Output

- Collects all non-None `StrategySignal` objects
- Sorts by `signal.score` descending

### Audit logging

If an `AuditLogger` is provided, it records `SIGNAL_GENERATED` events with:

- symbol, strategy_id, signal_id
- score, confidence


