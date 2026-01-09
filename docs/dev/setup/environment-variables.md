# Environment Variables

## UI → Backend

- `STOCKPORT_API_URL`
  - **Purpose**: points the UI to the backend REST API
  - **Default**: `http://localhost:8001`

## Authentication (developer mode)

In the Streamlit v5 UI (`ui/app_v5.py`) developer mode disables authentication using:

- `ENABLE_AUTHENTICATION=false`
- `DISABLE_AUTH=true`

If you enable authentication in your deployment, ensure these are not forced in production.


