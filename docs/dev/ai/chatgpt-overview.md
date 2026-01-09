# ChatGPT overview (for AI assistants)

This page is a high-level map for AI assistants (and new developers) to quickly find where things are implemented.

## What Stockport does

- Fetches market data via providers
- Runs multiple strategies to produce signals/opportunities
- Applies capital/risk gating to convert signals into decisions
- Optionally executes trades via broker integrations
- Publishes state and explanations to the Streamlit UI

## Where to look for key features

- **System wiring**: `backend/integration/system_integrator.py`
- **Scanner**: `backend/scanners/market_scanner.py`
- **Strategies**: `backend/strategies/strategies/`
- **Strategy evaluation**: `backend/strategies/evaluator.py`
- **Decision engine**: `backend/core/decision_engine.py`
- **Risk engine**: `backend/risk/risk_engine.py`
- **Position sizing**: `backend/capital/position_sizer.py`
- **Execution**: `backend/execution/` (brokers + order lifecycle)
- **Providers**: `services/data_providers/` and `backend/data/providers/` (router/validation)
- **UI**: `ui/`
- **Docs**:
  - User docs: `docs/` (served via `mkdocs-user.yml`)
  - Dev docs: `docs/dev/` (served via `mkdocs.yml`)

## Primary docs

- Deep, comprehensive guide: [ChatGPT comprehensive guide](../CHATGPT_COMPREHENSIVE_GUIDE.md)
- Architecture: [Architecture overview](../architecture/overview.md) and [System design](../architecture/system-design.md)
- APIs: [REST API](../api/rest-api.md) and [WebSocket API](../api/websocket-api.md)


