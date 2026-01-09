# WebSocket API

Some versions of Stockport support a WebSocket stream for real-time updates.

In the current UI codebase, the primary approach is **polling-first** (see `ui/services/polling_service.py`), with WebSocket support available via `ui/services/websocket_client.py` when configured.

See also: `api.md`.


