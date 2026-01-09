# Components

This page gives a practical map of Stockport’s major components and where to find them.

## UI (Streamlit Trading OS)

- **Entry point**: `app.py` → `ui/app_v5.py`
- **Workspaces**: `ui/workspaces/`
  - `insight.py`, `discover.py`, `decide.py`, `execute.py`, `review.py`
- **Reusable UI components**: `ui/components/`
  - Charts: `ui/components/charts/`
  - Visual: `ui/components/visual/`
  - Layout helpers: `ui/components/layout/`
- **Theme**: `ui/theme/`

## UI services

The UI is intentionally “a new lens, not a new brain”.

- REST client: `ui/services/api_client.py`
- UI data facade: `ui/services/ui_data_service.py`
- Derived UI metrics: `ui/services/metric_deriver.py`

## Backend + core domain

Depending on your branch/version, the backend is implemented under:

- `backend/` (API surfaces and orchestration)
- `core/`, `services/`, `models/` (business logic, indicators, models)
- `config/` (configuration + constants)

## Cross-cutting concerns

- Logging: `utils/debug_utils.py`
- Exceptions: `exceptions/`


