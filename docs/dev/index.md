# Stockport Developer Documentation

Welcome to the Stockport developer documentation.

## What is Stockport?

Stockport is an automated stock analysis and trading system built around an **always-on backend** and a **Streamlit Trading OS UI**. The backend continuously fetches market data, generates signals across multiple strategies, applies capital + risk constraints, and (optionally) executes trades.

## Start here

- **Setup (dev)**: Start with [Getting started (dev)](GETTING_STARTED.md), then use the [Setup section](setup/prerequisites.md).
- **Architecture**: Start with [Architecture overview](architecture/overview.md) and [System design](architecture/system-design.md).
- **API**: See [REST API](api/rest-api.md) and [WebSocket API](api/websocket-api.md).

## Key concepts

- **Event-driven**: Major subsystems communicate via events (e.g., Redis pub/sub).
- **Capital + risk gating**: Signals are not decisions; decisions are filtered by risk and available capital.
- **Explainability-first**: The system aims to expose “why” a signal/decision was produced.

## For AI assistants

See [ChatGPT comprehensive guide](CHATGPT_COMPREHENSIVE_GUIDE.md) for a full system summary oriented around “where is X implemented?” and “how does the flow work?”.


