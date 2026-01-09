# Strategy system (overview)

This section documents how Stockport loads strategies, evaluates them on market data, and produces signals/opportunities.

## Code map

- Strategy base class: `backend/strategies/base_strategy.py`
- Registry/loader: `backend/strategies/registry.py`, `backend/strategies/loader.py`
- Evaluator/orchestrator: `backend/strategies/evaluator.py`
- Strategy implementations: `backend/strategies/strategies/*.py`

## Pipeline (high level)

1. Load enabled strategies
2. Fetch/prepare market data
3. Each strategy evaluates and emits candidate signals
4. Evaluator scores/normalizes and ranks
5. Downstream systems apply risk/capital gates before execution

## Next pages

Read the deep dives in this section to see exact method contracts and file-level logic.


