# Adding a new strategy

This guide shows how to add a new strategy in a way that is testable and compatible with the evaluator.

## Where strategies live

- Implementations: `backend/strategies/strategies/`
- Base contract: `backend/strategies/base_strategy.py`
- Registration/loading: `backend/strategies/registry.py`, `backend/strategies/loader.py`

## Steps (high level)

1. Create a new strategy file under `backend/strategies/strategies/`
2. Implement the required interface from the base strategy
3. Register the strategy so the loader can instantiate it
4. Add tests with mocked data
5. Add documentation:
   - User page under `docs/strategies/`
   - Dev page under `docs/dev/strategy-system/strategies/`


