# Registry & loader

This page documents how strategies are discovered, registered, and instantiated.

## Implementation files

- `backend/strategies/registry.py`
- `backend/strategies/loader.py`

## Responsibilities (high level)

- Registry: defines available strategies and metadata
- Loader: creates instances based on configuration (enabled/disabled, parameters)

## Strategy registry (as implemented)

`StrategyRegistry` stores:

- `strategies: Dict[str, BaseStrategy]`
- `strategy_status: Dict[str, str]` (strategy_id → status)

Key behaviors:

- `register(strategy)`: adds the strategy and records its status
- `get_active()`: returns only strategies whose status is `"active"`
- `set_status(strategy_id, status)`: updates the status used for filtering

## Strategy loader (as implemented)

`StrategyLoader` loads YAML/JSON definitions and instantiates strategy classes based on `strategy.type`.

Current supported types in code:

- `trend_following`
- `momentum`

After instantiation it applies:

- `strategy.market_regimes` from `strategy.market_regimes`
- `strategy.exclude_regimes` from `strategy.exclude_regimes`

!!! note
    Additional strategy classes exist under `backend/strategies/strategies/`, but are not yet wired into `StrategyLoader` by type.


