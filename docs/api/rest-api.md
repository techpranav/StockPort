# REST API

The Streamlit UI uses a REST API client in `ui/services/api_client.py`.

## Base URL

- Configured by `STOCKPORT_API_URL`
- Default: `http://localhost:8001`

## Common endpoints (as used by UI)

> Note: exact availability depends on backend version.

- `GET /status`
- `GET /positions`
- `GET /orders`
- `GET /capital/overview`
- `GET /opportunities`
- `GET /strategies/performance`
- `GET /market/state`
- `GET /data/health`

See also: `api.md`.


