# Directory structure

This page explains the repo layout and where to find key logic.

## Top-level map (high signal)

- `backend/`: always-on backend services (APIs, workers, strategy engine)
- `services/`: analysis services (providers, indicators, signals, risk)
- `core/`: orchestration layer (batch/parallel analysis)
- `models/`: shared domain models (signals, risk metrics, stock data)
- `ui/`: Streamlit UI (Trading OS workspaces, components, theming)
- `config/`: configuration and constants (single source of truth)
- `utils/`: logging, caching, helpers
- `docs/`: user documentation (MkDocs user site)
- `docs/dev/`: developer documentation (MkDocs dev site)

## Where to look for…

- **Strategies**: `backend/strategies/strategies/`
- **Strategy evaluation/orchestration**: `backend/strategies/`
- **Provider implementations**: `services/data_providers/`
- **UI navigation/workspaces**: `ui/`
- **API endpoints**: `docs/dev/api/` (docs) and backend API code (implementation)


