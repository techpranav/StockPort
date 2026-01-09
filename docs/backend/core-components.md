# Core Components

This is a developer-facing map of backend responsibilities. Exact module names can differ across branches, but the system is conceptually consistent.

## Orchestration

The orchestrator coordinates:

- data refresh
- strategy evaluation
- risk checks
- order creation/execution

See: `APPLICATION_OVERVIEW.md`, `STOCKPORT_V4_COMPLETE.md`.

## Services

Backend services are generally organized around:

- **data providers** (market data sources)
- **analyzers/indicators**
- **signal generation**
- **risk management**
- **execution**

See: `services.md` and `services/` folder.


