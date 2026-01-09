# Base strategy

This page documents the strategy interface and expectations.

## Implementation file

`backend/strategies/base_strategy.py`

## Core interface

All strategies inherit from `BaseStrategy` and must implement:

- `evaluate(opportunity, market_state=None, ...) -> Optional[StrategySignal]`
- `get_entry_conditions() -> List[Dict[str, Any]]`
- `get_exit_conditions() -> Dict[str, Any]`

## Regime gating

`BaseStrategy.is_applicable(market_regime: str) -> bool` implements:

- If the regime is in `exclude_regimes` → **not applicable**
- Else if `market_regimes` is non-empty → only applicable if the current regime is in that list
- Else (default) → applicable to all regimes

## Status

The base class tracks a simple string status:

- `active`
- `paused`
- `disabled`

The registry uses this status to decide which strategies run.

## What every strategy must do (behavior expectations)

- Accept validated market data for a symbol/timeframe
- Calculate required indicators/patterns
- Produce one or more candidate signals/opportunities
- Provide explainability fields (why this signal exists)

## Notes

Some strategies accept `historical_data` (e.g., support/resistance computation). The evaluator detects this via `inspect.signature()` and passes it when supported.


