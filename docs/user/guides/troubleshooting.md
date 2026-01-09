# Troubleshooting (User)

## I see “no opportunities” / “no signals”

Common causes:

- The scanner has not produced any candidates yet.
- Filters are too strict (try lowering confidence/liquidity thresholds).
- The backend is not running or is unreachable.

## The UI loads but data looks stale

Check:

- **Insight → System Health** provider tiles for WARNING/ERROR.
- Backend availability (see developer docs if you need to start services).

## I get API connection errors

This typically means the backend REST API is not reachable.

- Ensure backend is running (default: `http://localhost:8001`)
- Ensure Streamlit UI is running (default: `http://localhost:8501`)


