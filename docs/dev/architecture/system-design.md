# System Design

This page describes how Stockport is organized and why.

## Layering

- **UI layer (`ui/`)**: Streamlit pages/workspaces + visual components.
- **UI services (`ui/services/`)**: REST client + metric derivations for display.
- **Backend API (`backend/...`)**: the UI’s integration surface.
- **Core trading logic (`core/`, `services/`)**: analysis, scanning, decisions.

## The Trading OS UI model (v5)

Stockport v5’s UI is organized into workspaces:

- Insight → context + health
- Discover → opportunities
- Decide → rationale + risk–reward
- Execute → order flow + execution quality
- Review → performance + learning

This design keeps the UI **signal-first** and avoids “dashboard noise”.

## Defensive defaults

The UI is designed to degrade gracefully:

- If backend is unavailable, services return safe defaults where possible.
- Empty states are intentional and calm.
- Errors are surfaced as user-facing notifications rather than broken layouts.


