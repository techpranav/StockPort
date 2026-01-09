# Frontend Overview (Streamlit)

Stockport’s frontend is a Streamlit application designed as a **Trading OS**.

## Entry points

- `app.py` delegates to `ui/app_v5.py`
- Workspaces are rendered via Streamlit tabs:
  - Insight / Discover / Decide / Execute / Review

## Responsibilities

- Present backend state in a signal-first layout
- Derive display-only metrics (no new brain)
- Handle empty/error states gracefully


