# Backend Overview

The backend is responsible for:

- Market data ingestion and validation
- Strategy/scanner evaluation
- Capital + risk enforcement
- Order generation and execution
- Persistent state and audit logging (depending on setup)

The Streamlit UI is intentionally a **viewer/control surface**, not the engine.

## Key concepts

- **Market state**: regime/volatility/breadth context used for decision-making.
- **Opportunities**: scanner outputs (candidates).
- **Signals**: opportunities shaped for action/triage.
- **Orders**: execution requests and lifecycle tracking.

## Where to look

- `backend/` for API surfaces and orchestration (varies by branch)
- `core/`, `services/`, `models/` for domain logic
- `config/` for configuration/constants


