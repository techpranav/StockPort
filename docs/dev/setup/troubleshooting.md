# Troubleshooting (Setup)

## Backend not reachable from UI

Symptoms:

- UI shows connection warnings
- No positions/orders/opportunities load

Checks:

- Backend is running on `STOCKPORT_API_URL` (default `http://localhost:8001`)
- No firewall rules blocking localhost ports

## Streamlit UI not loading

Checks:

- Run: `streamlit run app.py`
- Default UI URL: `http://localhost:8501`
- If ports are in use, stop processes and retry (see [Port management](../operations/port-management.md))

## Redis issues

If your deployment uses Redis and it is down, some backend subsystems may degrade.
See [Redis setup](../REDIS_SETUP.md).


