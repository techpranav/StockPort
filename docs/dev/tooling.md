# Development principles (tool motto)

This page captures the project’s “motto” for engineering changes and how to work safely.

## Motto

**Stability over speed. Backward compatibility by default. No silent behavior changes.**

## Non-negotiables

- No secrets in code (use env vars / `.env`)
- No `print()` for production logging (use `utils/debug_utils.py`)
- Validate external data (missing candles, NaNs, bad ticks)
- Prefer small, localized changes over large rewrites
- Add documentation whenever behavior changes

## How to work on Stockport

- **Start with the flow**: scanner → strategies → decisions → execution → UI updates
- **Make changes testable**: inject providers/brokers; mock external calls in tests
- **Observe health**: provider health should gate downstream actions

## When you add a new module

- Add configuration to `config/app_config.py`
- Add constants to `config/constants/`
- Add docs:
  - User docs under `docs/`
  - Dev docs under `docs/dev/`


