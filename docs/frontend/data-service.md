# UI Data Service Layer

The UI uses a small service layer to interact with the backend.

## Files

- `ui/services/api_client.py`: HTTP client + endpoint wrappers
- `ui/services/ui_data_service.py`: user-facing data facade
- `ui/services/metric_deriver.py`: derived metrics computed in the UI

## Design intent

- Keep backend APIs stable.
- Allow UI evolution by computing derived, display-only metrics in the UI.
- Degrade gracefully when backend endpoints are missing/unavailable.


